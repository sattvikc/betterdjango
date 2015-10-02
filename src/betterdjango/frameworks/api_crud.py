from betterdjango.frameworks import api

# TODO: Add exception handling
class CRUDHelper:
    def __init__(self, 
            model=None,
            fields=None,
            pk_field='pk',
            fk_field_map={'_default': 'pk'},
            filter_callback=None,
            add_callback=None
        ):
        self.model = model
        self.fields = fields
        self.pk_field = pk_field
        self.fk_field_map = fk_field_map
        self.filter_callback = filter_callback
        self.add_callback = add_callback
        self._fks = {}

        # Read the field properties
        for f in self.fields:
            mf = self.model._meta.get_field(f)
            if mf.__class__.__name__ == 'ForeignKey':
                self._fks[f] = mf

    def set_property(self, inst, field, value):
        if field in self._fks:
            fkf = self.fk_field_map.get(field, self.fk_field_map.get('_default', 'pk'))
            value = self._fks[field].related_model.objects.get(**{fkf: value})
            setattr(inst, field, value)
        else:
            setattr(inst, field, value)

    def add(self, request, **kwargs):
        nkwargs = {}
        for f in self.fields:
            if f in kwargs:
                nkwargs[f] = kwargs[f]
        inst = self.model()
        
        for f in nkwargs:
            self.set_property(inst, f, nkwargs[f])

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
                self.set_property(inst, f, kwargs[f])
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
        fk_field_map={'_default': 'pk'},
        filter_callback=None,
        add_callback=None,

        version='1.0',
        namespace='',
        api_names=('add', 'update', 'delete', 'list', 'get'),
    ):
    helper = CRUDHelper(model, fields, pk_field, fk_field_map, filter_callback, add_callback)
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
