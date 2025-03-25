from aiogram.utils.formatting import Bold, as_list, as_marked_section

categories = ['Tea', 'Accessories', 'Herbal', 'Green Tea', 'Black Tea', 'Matcha', 'Teapots', 'Tea Sets']

description_for_info_pages = {
    'main': 'Welcome!',
    'about': 'Tea Shop Home.\nWorking hours - 24/7.',
    'payment': as_marked_section(
        Bold('Payment options:'),
        'Card in bot',
        'Upon receipt, card/cash',
        'In-store',
        marker='✅ ',
    ).as_html(),
    'shipping': as_list(
        as_marked_section(
            Bold('Delivery/order options:'),
            'Courier',
            'Self-pickup (I will come and pick it up)',
            'I will drink tea at your place (I will come right now)',
            marker='✅ ',
        ),
        as_marked_section(Bold('Not allowed:'), 'Mail', 'Pigeons', marker='❌ '),
        sep='\n----------------------\n',
    ).as_html(),
    'catalog': 'Categories:',
    'cart': 'Your cart is empty!',
    'order': 'Check the order'
}
