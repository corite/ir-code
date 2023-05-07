class ScalarTransformer:

    def __init__(self, transformer, scalar):
        self.transformer = transformer
        self.scalar = scalar

    def transform(self, topics_and_res):
        res = self.transformer.transform(topics_and_res)
        res['score'] = self.scalar * res['score']
        return res

    def get_parameter(self, param):
        if param == 'scalar':
            return self.scalar
        raise Exception('invalid param')

    def set_parameter(self, param_name, value):
        if param_name == 'scalar':
            self.scalar = value
        else:
            raise Exception('invalid param')
