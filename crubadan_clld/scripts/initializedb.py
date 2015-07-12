# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import sys

from clld.scripts.util import initializedb, Data
from clld.db.meta import DBSession
from clld.db.models import common

import crubadan_clld
from crubadan_clld import models

import os
import codecs
from path import Path


# These are the files that will be lifted from the
# root crubadan directory and packaged into zip
# files for each language.
#
# format: [(NAME_IN_DATA_DIR, NAME_IN_ZIP_FILE)]
# 
# The files that go in the zip file automatically
# get the relevant language code prepended
# (e.g. "eng-testdata.txt")
#
packageFiles = [('TESTDATA', 'testdata.txt'),
                ('SOMETHING', 'something.txt')]

rootDataDir = '/data/crubadan'
rootClldDir = '/data/crubadan-clld'


def prepSysDirs():
    # os.system('rm -rf /data/crubadan-clld/*')
    os.system('if [ ! -d "' + rootClldDir + '" ]; then mkdir ' + rootClldDir + '; fi')
    os.system('if [ ! -d "' + rootClldDir + '/files" ]; then mkdir ' + rootClldDir + '/files; fi')

def fillTable(dbsession):
    langs = os.listdir(rootDataDir)
    c = 1
    for lang in langs:
        fname = rootDataDir + '/' + lang + '/' + 'EOLAS'
        mname = rootClldDir + '/metadata/' + lang + '.txt'
        trigfname = rootDataDir + '/' + lang + '/' + 'SAMPSENTS'
        if (os.path.isfile(fname)):
            f = codecs.open(fname, encoding='utf-8')
            fm = codecs.open(mname, encoding='utf-8')
            t = codecs.open(trigfname, encoding='utf-8')
            dic = {}

            # Read all ordinary data fields
            for line in f:
                parseAdd(line,dic,'')

            # Read all codata fields generated by that other script
            for line in fm:
                parseAdd(line,dic,'m_')

            # Add the path to the (not-yet-existant) dist zipfile to
            # the database
            dfile = models.WritingSystem_files(
                pk = lang,
                id = lang,
                name = lang,
                description = lang,
            )

            # Create the dist zipfile and store it in the right place
            z = lang + '.zip'
            # os.system('mkdir ' + lang)
            # os.system('cp doc/zip_file_LICENSE ' + lang + '/LICENSE')
            # for (sysFile,zipFile) in packageFiles:
            #     qSysFile = rootDataDir + '/' + lang + '/' + sysFile
            #     qZipFile = lang + '/' + lang + '-' + zipFile
            #     os.system('cp ' + qSysFile + ' ' + qZipFile)
            # os.system('zip -qr ' + z + ' ' + lang)
            # os.system('mv ' + z + ' ' + rootClldDir + '/files/' + z)
            # os.system('rm -r ' + lang)

            # Fill the database model
            ws = models.WritingSystem(

                # System stuff
                pk = lang,
                id = lang,
                jsondata = dic,
                name = dic[u'name_english'],
                description = dic[u'classification'],

                # Main data file
                eng_name = dic[u'name_english'],
                native_name = dic[u'name_native'],
                bcp47 = lang,
                iso6393 = dic[u'ISO_639-3'],
                country = dic[u'country'],
                script = dic[u'script'],
                parent_ws = dic[u'parent'],
                child_ws = dic[u'children'],
                ling_classification = dic[u'classification'],
                ethnologue_name = dic[u'ethnologue'],
                glottolog_name = dic[u'glottolog'],
            )

            dfile.object = ws
            
            dbsession.add(dfile)
            dbsession.add(ws)
    
            print 'Added ' + lang + ' ...'
            c += 1

def parseAdd(line,dic,prefix):
    if (line[0] != u'#'):
        (key,d,value) = line.partition(u' ')
        p_key = prefix + key
        if (value == u"XXX\n"):
            dic[p_key] = u"(Unknown)\n"
        elif ((value == u"none\n") or (value == u"\n")):
            dic[p_key] = u"None\n"
        else:
            dic[p_key] = value

def main(args):
    data = Data()

    dataset = common.Dataset(
        id= u'An Crúbadán',
        name= u'An Crúbadán',
        publisher_name="???",
        publisher_place="???",
        publisher_url="???",
        description="???",
        contact="???",
        license='http://creativecommons.org/licenses/by/4.0/', # ???
        jsondata={
            'license_icon': 'https://licensebuttons.net/l/by/4.0/88x31.png',
            'license_name': 'Creative Commons Attribution 4.0 International License',
            },
        domain='crubadan.org',
        )

    DBSession.add(dataset)
    DBSession.flush()

    editor = data.add(common.Contributor, "Kevin Scannell", id="Kevin Scannell", name="Kevin Scannell", email="kscanne@gmail.com")
    common.Editor(dataset=dataset, contributor=editor, ord=0)
    DBSession.flush()
    

## An example dataset declaration from http://sails.clld.org/
##
# 
#  dataset = common.Dataset(
#      id="SAILS",
#      name='SAILS Online',
#      publisher_name="Max Planck Institute for Evolutionary Anthropology",
#      publisher_place="Leipzig",
#      publisher_url="http://www.eva.mpg.de",
#      description="Dataset on Typological Features for South American Languages, collected 2009-2013 in the Traces of Contact Project (ERC Advanced Grant 230310) awarded to Pieter Muysken, Radboud Universiteit, Nijmegen, the Netherlands.",
#      domain='sails.clld.org',
#      published=date(2014, 2, 20),
#      contact='harald.hammarstroem@mpi.nl',
#      license='http://creativecommons.org/licenses/by-nc-nd/2.0/de/deed.en',
#      jsondata={
#          'license_icon': 'http://wals.info/static/images/cc_by_nc_nd.png',
#          'license_name': 'Creative Commons Attribution-NonCommercial-NoDerivs 2.0 Germany'})
#  DBSession.add(dataset)
#  DBSession.flush()
# 
#  editor = data.add(common.Contributor, "Harald Hammarstrom", id="Harald Hammarstrom", name="Harald Hammarstrom", email = "harald.hammarstroem@mpi.nl")
#  common.Editor(dataset=dataset, contributor=editor, ord=0)
#  DBSession.flush()
#  

    fillTable(DBSession)

def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodiucally whenever data has been updated.
    """


if __name__ == '__main__':
    prepSysDirs()
    initializedb(create=main, prime_cache=prime_cache)
    sys.exit(0)
