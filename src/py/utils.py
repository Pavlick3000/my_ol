from collections import defaultdict
from django.db import connection

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

    return root_items

# Группировка внутри дерева
def group_children(items):
    grouped = defaultdict(lambda: {
        'TotalQuantity': 0,
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
    })

    for item in items:
        key = (item['ComponentID'], item['ParentID'], item['Path'])

        grouped_item = grouped[key]

        # Обновляем поля (сохраняем первый попавшийся ненулевой вариант)
        for field in ['ComponentName', 'basic_unit', 'Level', 'CategoryName', 'CategoryParentName', 'CategoryGrandParentName']:
            if grouped_item[field] is None:
                grouped_item[field] = item.get(field)

        grouped_item['TotalQuantity'] += item.get('TotalQuantity', 0)

        for field in ['ComponentID', 'ComponentDbId', 'OrderItemID', 'ParentID', 'Path']:
            if grouped_item[field] is None:
                grouped_item[field] = item.get(field)

        grouped_item['children'].extend(item.get('children', []))

    result = []
    for val in grouped.values():
        val['children'] = group_children(val['children'])
        result.append(val)

    return result

