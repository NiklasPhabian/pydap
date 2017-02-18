"""The CITATION response.

The CITATION response is an unnoficial response used to return a citation of the dataset.

"""
import re

from pydap.lib import encode, __version__
from pydap.responses.lib import BaseResponse
from pydap.responses.das import das
from pydap.parsers import parse_ce, parse_selection, parse_projection
import collections
import datetime


class CitationResponse(BaseResponse):
    """The Citation response."""

    __version__ = __version__

    def __init__(self, dataset, request=None):        
        BaseResponse.__init__(self, dataset, request)

    def __iter__(self): 
        citation = Citation()                
        citation.from_attributes(self.dataset.attributes)                        
        citation.subsets_from_query_str(self.request.query_string)
        citation.intentifier_from_request(self.request)
        yield citation.as_text()
            
            
class Citation:
    def __init__(self):
        self.meta = collections.OrderedDict()
        self.meta['author'] = None
        self.meta['title'] = None
        self.meta['institution'] = None
        self.meta['date'] = None        
        self.meta['version'] = None        
        self.meta['url'] = None
        self.meta['accessed'] = datetime.datetime.now().strftime('%Y-%m-%d')
        self.meta['doi'] = None        
        self.meta['identifier'] = None
        self.subset = collections.OrderedDict()
        
    def intentifier_from_request(self, request):
        self.meta['identifier'] = request.application_url+request.path

    def from_attributes(self, attributes):                   
        self.meta['author'] = self.author_from_attributes(attributes)
        self.meta['title'] = self.title_from_attributes(attributes)        
        self.meta['institution'] = self.institution_from_attributes(attributes)
        self.meta['date'] = self.date_from_attributes(attributes)
        
    def institution_from_attributes(self, attributes):
        identifiers = ['institution', 'NC_GLOBAL.Institution']
        return self.find_attribute(identifiers, attributes)
    
    def title_from_attributes(self, attributes):
        identifiers = ['title', 'NC_GLOBAL.Title']
        return self.find_attribute(identifiers, attributes)
    
    def date_from_attributes(self, attributes):
        identifiers = ['NC_GLOBAL.DATE_CREATION']        
        return self.find_attribute(identifiers, attributes)        
    
    def author_from_attributes(self, attributes):
        identifiers = ['NC_GLOBAL.AUTHOR', 'AUTHOR']        
        return self.find_attribute(identifiers, attributes)        

    def find_attribute(self, identifiers, attributes):
        attribute = None        
        for attribute in attributes['NC_GLOBAL']:
            for identifier in identifiers:
                if identifier.lower() == attribute.lower():
                    return attributes['NC_GLOBAL'][attribute]
                        
    def add_subset_param(self, subset_param):                    
            self.subset[subset_param[0]] = ' '
            
    def subsets_from_query_str(self, query_string):        
        params = query_string.split(',')        
        for param in params: 
            param = param.replace('%3E', '>')            
            self.subset[param] = ''     
            
    def as_text(self):
        cit_text = '{'   
        cit_text += self.meta_text() 
        cit_text += self.subset_text() 
        cit_text += '\n}'
        return cit_text
    
    def as_bibtex(self):
        bib_text = '@ELECTRONIC{'
        for key in self.meta:
            bib_text += '\n\t'
            meta_text += key
            meta_text += ': {'
            meta_text += self.meta[key]
            meta_text += '},'
        meta_text = meta_text[:-1]
        meta_text += '\n}'
        
    def subset_text(self):
        if len(self.subset)>0:
            subset_text = '\n\tsubsetting: {'            
            for key in self.subset:
                subset_text += '\n\t\t'
                subset_text += key
            subset_text += '\n\t}'
            return subset_text
        else:
            return ''        

    def meta_text(self):
        meta_text = ''
        for key in self.meta:
            if self.meta[key]:                
                meta_text += '\n\t'
                meta_text += key
                meta_text += ': "'
                meta_text += self.meta[key]
                meta_text += '",'
        meta_text = meta_text[:-1]        
        return str(meta_text)


