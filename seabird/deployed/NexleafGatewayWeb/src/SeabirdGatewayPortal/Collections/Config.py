from mongoengine import Document, StringField

class Config(Document):
    title = StringField(required=True)
    xml = StringField(required=True)
    version = StringField(unique=True, required=True)
        
    def __unicode__(self):
        return '%s' % self.title
    

