from collections import defaultdict
from django.db import connection
from decimal import Decimal

# Получаем дерево из SQL процедуры
def get_specs_tree(orderId, itemId=None):
    with connection.cursor() as cursor:
        cursor.execute("SELECT TOP 1 _IDRRef FROM _Document400 WHERE id = %s", [orderId])
        order_data = cursor.fetchone()
        if not order_data:
            raise Exception(f"Заказ {orderId} не найден")

        cursor.execute("EXEC GetSpecsDetailsByOrderId %s, NULL, %s", [orderId, itemId])
        if not cursor.description:
            return []

        columns = [col[0] for col in cursor.description]
        result = []
        raw_rows = cursor.fetchall()

        for row in raw_rows:
            item = dict(zip(columns, [
                val.hex().lower() if isinstance(val, bytes) else val
                for val in row
            ]))
            item['children'] = []
            result.append(item)

    nodes = { (item['ComponentID'], item.get('ParentID'), item['Path']) : item for item in result }

    # Для оптимизации создадим индекс по ComponentID к ключам
    parent_index = defaultdict(list)
    for key in nodes:
        parent_index[key[0]].append(key)

    for key, node in nodes.items():
        parent_id = node.get('ParentID')
        if parent_id:
            possible_parents = parent_index.get(parent_id, [])
            parent_key = None
            for pk in possible_parents:
                if node['Path'].startswith(pk[2]):
                    parent_key = pk
                    break
            if parent_key:
                nodes[parent_key]['children'].append(node)

    root_items = [
        node for key, node in nodes.items()
        if not node.get('ParentID') or
           not any(k[0] == node.get('ParentID') and node['Path'].startswith(k[2]) for k in nodes)
    ]

    sort_tree(root_items)  # Сортировка дерева

    return root_items

# Группировка внутри дерева
def group_children(items):
    grouped = defaultdict(lambda: {
        'TotalQuantity': 0,
        'Qnt': None,
        'Requirement': None,
        'children': [],
        'items': [],
        'ComponentName': None,
        'basic_unit': None,
        'Level': 0,
        'CategoryName': None,
        'CategoryParentName': None,
        'CategoryGrandParentName': None,
        'ComponentID': None,
        'ComponentDbId': None,
        'OrderItemID': None,
        'ParentID': None,
        'Path': None,
        'QuantityPerUnit': None, # нов0508
    })

    for item in items:
        key = (item['ComponentID'], item['ParentID'], item['Path'])
        grouped_item = grouped[key]

        # Обновляем поля (сохраняем первый попавшийся ненулевой вариант)
        for field in ['ComponentName', 'basic_unit', 'Level', 'CategoryName', 'CategoryParentName', 'CategoryGrandParentName']:
            if grouped_item[field] is None:
                grouped_item[field] = item.get(field)

        if grouped_item['QuantityPerUnit'] is None:
            qpu = item.get('QuantityPerUnit')
            # механика: считать None/0 как отсутствующее значение; поменяйте условие при необходимости
            if qpu is not None:
                grouped_item['QuantityPerUnit'] = qpu

        grouped_item['TotalQuantity'] += item.get('TotalQuantity', 0)
        # grouped_item['Qnt'] += item.get('Qnt', 0)

        # Берём Qnt, если ещё не было
        if grouped_item['Qnt'] is None:
            grouped_item['Qnt'] = item.get('Qnt')

            # Берём Qnt, если ещё не было
            if grouped_item['Requirement'] is None:
                grouped_item['Requirement'] = item.get('Requirement')

        for field in ['ComponentID', 'ComponentDbId', 'OrderItemID', 'ParentID', 'Path']:
            if grouped_item[field] is None:
                grouped_item[field] = item.get(field)

        grouped_item['children'].extend(item.get('children', []))

    result = []
    for val in grouped.values():
        val['children'] = group_children(val['children'])
        result.append(val)

    return result

# TODO
#  1. Готово - Тултипы у иконок крестика и фильтра
#  2. Готово - Фильтр по категории должен сохраняться по кликам по дереву
#  3. В дереве должны подсвечиваться материалы с детьми (родители), в которых есть дефицит


# Сортировка дерева
def sort_tree(items):
    items.sort(
        key=lambda x: (
            len(x['children']) == 0,        # Сначала с детьми, потом без
            x.get('ComponentName', '').lower()  # Алфавитная сортировка, без учёта регистра
        )
    )
    for item in items:
        if item['children']:
            sort_tree(item['children'])

# Группировка таблицы материалов
def group_flat_materials(rows, columns):
    # grouped = defaultdict(lambda: {'TotalQuantity': Decimal(0)})

    grouped = defaultdict(lambda: {
        'TotalQuantity': Decimal(0),
        'Qnt': None,
        'Requirement': None,
        'CategoryName': None,
        'ComponentName': None,
        'basic_unit': None
    })

    for row in rows:
        row_dict = dict(zip(columns, row))

        key = (
            row_dict.get('ComponentName'),
            row_dict.get('basic_unit'),
            row_dict.get('CategoryName'),
        )

        group = grouped[key]

        group['ComponentName'] = row_dict.get('ComponentName')
        group['basic_unit'] = row_dict.get('basic_unit')
        group['TotalQuantity'] += row_dict.get('TotalQuantity') or Decimal(0)
        # group['CategoryName'] = row_dict.get('CategoryName')

        # Сохраняем CategoryName только если еще не сохранена
        if group['CategoryName'] is None and row_dict.get('CategoryName') is not None:
            group['CategoryName'] = row_dict.get('CategoryName')

        if group['Qnt'] is None and row_dict.get('Qnt') is not None:
            group['Qnt'] = row_dict.get('Qnt')

        if group['Requirement'] is None and row_dict.get('Requirement') is not None:
            group['Requirement'] = row_dict.get('Requirement')

    return [
        {
            'ComponentName': k[0],
            'basic_unit': k[1],
            'TotalQuantity': float(v['TotalQuantity']),
            'CategoryName': v['CategoryName'],
            'Qnt': v['Qnt'],
            'Requirement': v['Requirement']
        }
        for k, v in grouped.items()
    ]

