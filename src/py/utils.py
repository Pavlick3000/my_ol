from collections import defaultdict
from django.db import connection

# Группировка внутри дерева
def group_children(items):
    grouped = defaultdict(lambda: {
        'TotalQuantity': 0,
        'children': [],
        'items': []
    })

    for item in items:
        key = (item['ComponentName'], item['basic_unit'])
        grouped_item = grouped[key]

        grouped_item['ComponentName'] = item['ComponentName']
        grouped_item['basic_unit'] = item['basic_unit']
        grouped_item['Level'] = item.get('Level', 0)
        grouped_item['CategoryName'] = item.get('CategoryName')
        grouped_item['CategoryParentName'] = item.get('CategoryParentName')
        grouped_item['CategoryGrandParentName'] = item.get('CategoryGrandParentName')
        grouped_item['TotalQuantity'] += item.get('TotalQuantity', 0)

        # Ключевые поля (один раз)
        if 'ComponentID' not in grouped_item:
            grouped_item['ComponentID'] = item.get('ComponentID')
        if 'ComponentDbId' not in grouped_item:
            grouped_item['ComponentDbId'] = item.get('ComponentDbId')
        if 'OrderItemID' not in grouped_item:
            grouped_item['OrderItemID'] = item.get('OrderItemID')
        if 'ParentID' not in grouped_item:
            grouped_item['ParentID'] = item.get('ParentID')

        # Дети
        grouped_item['children'].extend(item.get('children', []))

    # Рекурсивная группировка
    result = []
    for val in grouped.values():
        val['children'] = group_children(val['children'])
        result.append(val)

    return result

# Получаем дерево из SQL процедуры
def get_specs_tree(orderId, itemId=None):
    with connection.cursor() as cursor:
        # Проверка существования заказа
        cursor.execute("SELECT TOP 1 _IDRRef FROM _Document400 WHERE id = %s", [orderId])
        order_data = cursor.fetchone()
        if not order_data:
            raise Exception(f"Заказ {orderId} не найден")

        # Выполнение хранимой процедуры
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

    # Построение иерархии
    from collections import defaultdict
    children_map = defaultdict(list)
    id_to_items = defaultdict(list)

    for item in result:
        component_id = item['ComponentID']
        parent_id = item.get('ParentID')
        id_to_items[component_id].append(item)

        if parent_id:
            children_map[parent_id].append(item)

    for parent_id, children in children_map.items():
        parent_items = id_to_items.get(parent_id, [])
        for parent_item in parent_items:
            parent_item['children'].extend(children)

    # Поиск корневых элементов
    root_items = [item for item in result if not item.get('ParentID') or item['ParentID'] not in id_to_items]

    return root_items



