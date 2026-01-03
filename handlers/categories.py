@router.callback_query(F.data.startswith("category_"))
async def category_selected(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[1])
    
    db: Session = next(get_db())
    user = db.query(User).filter(User.telegram_id == callback.from_user.id).first()
    
    if not user:
        await callback.answer()
        return
    
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == user.id
    ).first()
    
    if not category:
        await callback.answer("❌ Категория не найдена")
        return
    
    products = db.query(Product).filter(Product.category_id == category_id).all()
    
    if user.language == 'ru':
        text = f"📁 Категория: {category.name}\n\n"
        text += f"Товаров в категории: {len(products)}\n\n"
        
        if products:
            text += "Товары:\n"
            for idx, product in enumerate(products, 1):
                text += f"{idx}. {product.name} - {product.quantity} шт.\n"
        else:
            text += "В этой категории пока нет товаров."
    else:
        text = f"📁 Category: {category.name}\n\n"
        text += f"Products in category: {len(products)}\n\n"
        
        if products:
            text += "Products:\n"
            for idx, product in enumerate(products, 1):
                text += f"{idx}. {product.name} - {product.quantity} pcs.\n"
        else:
            text += "No products in this category yet."
    
    await callback.message.answer(text)
    await callback.answer()
