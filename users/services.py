import stripe
from config.settings import STRIPE_API_KEY

stripe.api_key = STRIPE_API_KEY


def create_stripe_product(product_data):
    """Создаёт продукт в Stripe"""
    try:
        stripe_product = stripe.Product.create(
            name=product_data['name'],
            description=product_data.get('description', '')
        )
        return stripe_product
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка при создании продукта в Stripe: {str(e)}")


def create_stripe_price(product_id, amount):
    """Создаёт цену продукта в Stripe"""
    try:
        price_in_kopecks = int(amount * 100)

        price = stripe.Price.create(
            currency="rub",
            unit_amount=price_in_kopecks,
            product=product_id
        )
        return price
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка при создании цены в Stripe: {str(e)}")


def create_stripe_session(price_id, success_url=None):
    """Создаёт сессию для оплаты в Stripe"""
    try:
        if not success_url:
            success_url = "http://127.0.0.1:8000/"

        session = stripe.checkout.Session.create(
            success_url=success_url,
            cancel_url="http://127.0.0.1:8000/",
            line_items=[{"price": price_id, "quantity": 1}],
            mode="payment",
        )
        return session.id, session.url
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка при создании сессии в Stripe: {str(e)}")


def retrieve_stripe_session(session_id):
    """Получает информацию о сессии из Stripe"""
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return session
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка при получении сессии из Stripe: {str(e)}")


def create_payment_in_stripe(payment):
    """Создает платеж в Stripe и возвращает данные для сохранения"""
    try:
        if payment.course:
            product_name = payment.course.title
            product_description = payment.course.description or ""
        elif payment.lesson:
            product_name = payment.lesson.title
            product_description = payment.lesson.description or ""
        else:
            raise ValueError("Не указан курс или урок для оплаты")

        stripe_product = create_stripe_product({
            'name': product_name,
            'description': product_description
        })

        stripe_price = create_stripe_price(stripe_product.id, float(payment.amount))

        session_id, session_url = create_stripe_session(stripe_price.id)

        return {
            'stripe_product_id': stripe_product.id,
            'stripe_price_id': stripe_price.id,
            'stripe_session_id': session_id,
            'stripe_payment_link': session_url
        }

    except Exception as e:
        raise Exception(f"Ошибка при создании платежа в Stripe: {str(e)}")
