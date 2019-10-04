import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker


rabbitmq_broker = RabbitmqBroker(url="amqp://admin:admin@container.ll-ap.cn:5672")
dramatiq.set_broker(rabbitmq_broker)


# @dramatiq.actor(queue_name='result')
def result(success=False, data=None, message=None):
    print({'success': success, 'data': data, 'message': message})
