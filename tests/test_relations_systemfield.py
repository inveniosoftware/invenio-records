# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Tests for relations system field."""

import pytest
from collections.abc import Iterable

from invenio_records.api import Record
from invenio_records.systemfields import PKRelation, RelationsField, \
    SystemFieldsMixin
from invenio_records.systemfields.relations import InvalidRelationValue, PKListRelation, \
    RelationsMapping


@pytest.fixture()
def languages(db):
    class Language(Record, SystemFieldsMixin):
        pass

    languages_data = (
        {'title': 'English', 'iso': 'en'},
        {'title': 'French', 'iso': 'fr'},
        {'title': 'Spanish', 'iso': 'es'},
        {'title': 'Italian', 'iso': 'it'},
    )

    languages = {}
    for l in languages_data:
        lang_rec = Language.create(l)
        languages[l['iso']] = lang_rec
    db.session.commit()
    return Language, languages


def test_relations_field_pk_relation(testapp, db, languages):
    """RelationsField tests for PKRelation."""

    Language, languages = languages
    en_lang = languages['en']
    fr_lang = languages['fr']

    class Record1(Record, SystemFieldsMixin):
        relations = RelationsField(
            language=PKRelation(
                key='language', attrs=['iso'], record_cls=Language),
        )

    # Class-field check
    assert isinstance(Record1.relations, RelationsField)
    assert isinstance(Record1.relations.language, PKRelation)

    # Empty initialization
    record = Record1({})
    assert record == {}
    assert isinstance(record.relations, RelationsMapping)
    assert callable(record.relations.language)
    assert record.relations.language() is None

    # Initialize from dictionary data
    record = Record1({'language': {'id': str(en_lang.id)}})
    res = record.relations.language()
    assert isinstance(res, Language)
    assert res == en_lang

    # Initialize from field data
    record = Record1({}, relations={'language': str(en_lang.id)})
    assert record['language']['id'] == str(en_lang.id)
    res = record.relations.language()
    assert isinstance(res, Language)
    assert res == en_lang

    # Set via record data
    record = Record1.create({})
    record['language'] = {'id': str(en_lang.id)}
    res = record.relations.language()
    assert isinstance(res, Language)
    assert res == en_lang
    record.commit()  # validates
    res = record.relations.language()
    assert isinstance(res, Language)
    assert res == en_lang

    record['language'] = {'id': 'invalid'}
    with pytest.raises(InvalidRelationValue):
        record.commit()  # fails validation

    # Set via attribute
    record = Record1.create({})
    record.relations.language = str(en_lang.id)
    assert record['language']['id'] == str(en_lang.id)
    res = record.relations.language()
    assert isinstance(res, Language)
    assert res == en_lang

    # Update existing value
    record.relations.language = str(fr_lang.id)
    assert record['language']['id'] == str(fr_lang.id)
    res = record.relations.language()
    assert isinstance(res, Language)
    assert res == fr_lang

    # Set invalid value
    with pytest.raises(InvalidRelationValue):
        record.relations.language = 'invalid'
    # Check that old value is still there
    assert record['language']['id'] == str(fr_lang.id)
    res = record.relations.language()
    assert isinstance(res, Language)
    assert res == fr_lang

    # Dereference relation
    record.relations.language.dereference()
    assert record['language'] == {
        'id': str(fr_lang.id),
        'iso': 'fr',  # only stores the "iso" field
    }

    # Commit clean dereferened fields
    record.commit()
    assert record['language'] == {'id': str(fr_lang.id)}

    # Commit to DB and refetch
    db.session.commit()
    record = Record1.get_record(record.id)
    assert record['language'] == {'id': str(fr_lang.id)}
    res = record.relations.language()
    assert isinstance(res, Language)
    assert res == fr_lang

    # Clear field
    record.relations.language = None
    assert 'language' not in record
    assert record.relations.language() is None
    record.commit()


def test_relations_field_pk_list_relation(testapp, db, languages):
    """RelationsField tests for PKListRelation."""

    Language, languages = languages
    en_lang = languages['en']
    fr_lang = languages['fr']
    es_lang = languages['es']

    class Record1(Record, SystemFieldsMixin):
        relations = RelationsField(
            languages=PKListRelation(
                key='languages', attrs=['iso'], record_cls=Language),
        )

    # Class-field check
    assert isinstance(Record1.relations, RelationsField)
    assert isinstance(Record1.relations.languages, PKListRelation)

    # Empty initialization
    record = Record1({})
    assert record == {}
    assert isinstance(record.relations, RelationsMapping)
    assert callable(record.relations.languages)
    assert record.relations.languages() is None

    # Initialize from dictionary data
    record = Record1({'languages': [{'id': str(en_lang.id)}]})
    res_iter = record.relations.languages()
    assert isinstance(res_iter, Iterable)
    res = next(res_iter)
    assert res == en_lang

    # Initialize from field data
    record = Record1({}, relations={'languages': [str(en_lang.id)]})
    assert record['languages'] == [{'id': str(en_lang.id)}]
    res_iter = record.relations.languages()
    assert isinstance(res_iter, Iterable)
    res = next(res_iter)
    assert res == en_lang

    # Set via record dictionary data
    record = Record1.create({})
    record['languages'] = [{'id': str(en_lang.id)}]
    res_iter = record.relations.languages()
    assert isinstance(res_iter, Iterable)
    res = next(res_iter)
    assert res == en_lang
    record.commit()  # validates
    res_iter = record.relations.languages()
    assert isinstance(res_iter, Iterable)
    res = next(res_iter)
    assert res == en_lang

    record['languages'] = {'id': 'invalid'}
    with pytest.raises(InvalidRelationValue):
        record.commit()  # fails validation

    # Set via attribute
    record = Record1.create({})
    record.relations.languages = [str(en_lang.id)]
    assert record['languages'][0]['id'] == str(en_lang.id)
    res_iter = record.relations.languages()
    assert isinstance(res_iter, Iterable)
    res = next(res_iter)
    assert res == en_lang

    # Update existing value
    record.relations.languages = [str(fr_lang.id)]
    assert record['languages'][0]['id'] == str(fr_lang.id)
    res_iter = record.relations.languages()
    assert isinstance(res_iter, Iterable)
    res = next(res_iter)
    assert res == fr_lang

    # Set invalid value
    for v in ('invalid', ['invalid']):
        with pytest.raises(InvalidRelationValue):
            record.relations.languages = v
        # Check that old value is still there
        assert record['languages'][0]['id'] == str(fr_lang.id)
        res_iter = record.relations.languages()
        assert isinstance(res_iter, Iterable)
        res = next(res_iter)
        assert res == fr_lang

    # Dereference relation
    record.relations.languages.dereference()
    assert record['languages'] == [{
        'id': str(fr_lang.id),
        'iso': 'fr',  # only stores the "iso" field
    }]

    # Commit clean dereferened fields
    record.commit()
    assert record['languages'] == [{'id': str(fr_lang.id)}]

    # Commit to DB and refetch
    db.session.commit()
    record = Record1.get_record(record.id)
    assert record['languages'] == [{'id': str(fr_lang.id)}]
    res_iter = record.relations.languages()
    assert isinstance(res_iter, Iterable)
    res = next(res_iter)
    assert res == fr_lang

    # Clear field
    record.relations.languages = None
    assert 'languages' not in record
    assert record.relations.languages() is None
    record.commit()
