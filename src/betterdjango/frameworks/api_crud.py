from betterdjango.frameworks import api

# TODO: Add exception handling
class CRUDHelper:
    def __init__(self, 
            model=None,
            fields=None,
            pk_field='pk',
            filter_callback=None,
            add_callback=None
        ):
        self.model = model
        self.fields = fields
        self.pk_field = pk_field
        self.filter_callback = filter_callback
        self.add_callback = add_callback

    def add(self, request, **kwargs):
        nkwargs = {}
        for f in self.fields:
            if f in kwargs:
                nkwargs[f] = kwargs[f]
        inst = self.model(**nkwargs)
        if not self.add_callback is None:
            self.add_callback(request, inst)
        inst.save()
        return inst

    def update(self, request, **kwargs):
        # TODO: Add more validation
        if not self.pk_field in kwargs:
            raise Exception('Missing query field [%s]' % self.pk_field)
        if self.filter_callback is None:
            inst = self.model.objects.get(**{self.pk_field: kwargs[self.pk_field]})
        else:
            inst = self.model.objects.filter(self.filter_callback(request)).get(**{self.pk_field: kwargs[self.pk_field]})
        for f in self.fields:
            if f in kwargs:
                setattr(inst, f, kwargs[f])
        inst.save()
        return inst

    def delete(self, request, **kwargs):
        # TODO: Add more validation
        if not self.pk_field in kwargs:
            raise Exception('Missing query field [%s]' % self.pk_field)
        if self.filter_callback is None:
            inst = self.model.objects.get(**{self.pk_field: kwargs[self.pk_field]})
        else:
            inst = self.model.objects.filter(self.filter_callback(request)).get(**{self.pk_field: kwargs[self.pk_field]})
        inst.delete()


    def list(self, request):
        if self.filter_callback is None:
            return self.model.objects.all()
        else:
            return self.model.objects.filter(self.filter_callback(request))

    def get(self, request, **kwargs):
        # TODO: Add more validation
        if not self.pk_field in kwargs:
            raise Exception('Missing query field [%s]' % self.pk_field)
        if self.filter_callback is None:
            return self.model.objects.get(**{self.pk_field: kwargs[self.pk_field]})
        else:
            return self.model.objects.filter(self.filter_callback(request)).get(**{self.pk_field: kwargs[self.pk_field]})


def create_crud(
        model=None,
        fields=None,
        pk_field='pk',
        filter_callback=None,
        add_callback=None,

        version='1.0',
        namespace='',
        api_names=('add', 'update', 'delete', 'list', 'get'),
    ):
    helper = CRUDHelper(model, fields, pk_field, filter_callback, add_callback)
    api.provider.register(
            version=version,
            namespace=namespace,
            api_name=api_names[0],
            http_methods=['GET'],
        )(helper.add)

    api.provider.register(
            version=version,
            namespace=namespace,
            api_name=api_names[1],
            http_methods=['GET'],
        )(helper.update)

    api.provider.register(
            version=version,
            namespace=namespace,
            api_name=api_names[2],
            http_methods=['GET'],
        )(helper.delete)

    api.provider.register(
            version=version,
            namespace=namespace,
            api_name=api_names[3],
            http_methods=['GET'],
        )(helper.list)

    api.provider.register(
            version=version,
            namespace=namespace,
            api_name=api_names[4],
            http_methods=['GET'],
        )(helper.get)
