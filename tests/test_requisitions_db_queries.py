import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import IntegrityError
from src.db_queries import requisitions
from src.models import ItemTypes, ItemTypeCreate, ItemTypeInfo

@pytest.fixture
def mock_session():
    return MagicMock()

def test_add_item_type_to_db_success(mock_session):
    item_type_data = MagicMock(spec=ItemTypeCreate)
    item_type_data.model_dump.return_value = {'name': 'TestType'}
    mock_item_type = MagicMock(spec=ItemTypes)
    with patch('src.db_queries.requisitions.ItemTypes', return_value=mock_item_type):
        result = requisitions.add_item_type_to_db(mock_session, item_type_data)
        mock_session.add.assert_called_once_with(mock_item_type)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_item_type)
        assert result == mock_item_type

def test_add_item_type_to_db_integrity_error(mock_session):
    item_type_data = MagicMock(spec=ItemTypeCreate)
    item_type_data.model_dump.return_value = {'name': 'TestType'}
    mock_item_type = MagicMock(spec=ItemTypes)
    integrity_error = IntegrityError('statement', 'params', Exception('orig'))
    mock_session.add.side_effect = integrity_error
    with patch('src.db_queries.requisitions.ItemTypes', return_value=mock_item_type):
        with pytest.raises(IntegrityError):
            requisitions.add_item_type_to_db(mock_session, item_type_data)
        mock_session.rollback.assert_called_once()

def test_get_item_type_by_id_success(mock_session):
    mock_item_type = MagicMock(spec=ItemTypes)
    mock_exec = MagicMock()
    mock_exec.first.return_value = mock_item_type
    mock_session.exec.return_value = mock_exec

    result = requisitions.get_item_type_by_id(mock_session, 1)
    assert result == mock_item_type
    mock_session.exec.assert_called_once()

def test_get_item_type_by_id_exception(mock_session):
    mock_session.exec.side_effect = Exception("DB error")
    with pytest.raises(Exception):
        requisitions.get_item_type_by_id(mock_session, 1)

def test_get_item_type_list_from_db_success(mock_session):
    mock_item_type1 = MagicMock(spec=ItemTypes)
    mock_item_type2 = MagicMock(spec=ItemTypes)
    mock_exec = MagicMock()
    mock_exec.all.return_value = [mock_item_type1, mock_item_type2]
    mock_session.exec.return_value = mock_exec

    result = requisitions.get_item_type_list_from_db(mock_session)
    assert result == [mock_item_type1, mock_item_type2]
    mock_session.exec.assert_called_once()

def test_get_item_type_list_from_db_exception(mock_session):
    mock_session.exec.side_effect = Exception("DB error")
    with pytest.raises(Exception):
        requisitions.get_item_type_list_from_db(mock_session)

def test_update_item_type_in_db_not_found(mock_session):
    item_type_data = MagicMock(spec=ItemTypeInfo)
    item_type_data.id = 1
    mock_exec = MagicMock()
    mock_exec.first.return_value = None
    mock_session.exec.return_value = mock_exec

    with pytest.raises(Exception):
        requisitions.update_item_type_in_db(mock_session, item_type_data)

def test_update_item_type_in_db_success(mock_session):
    item_type_data = MagicMock(spec=ItemTypeInfo)
    item_type_data.id = 1
    item_type_data.model_dump.return_value = {'id': 1, 'name': 'UpdatedType'}
    mock_item_type = MagicMock(spec=ItemTypes)
    mock_exec = MagicMock()
    mock_exec.first.return_value = mock_item_type
    mock_session.exec.return_value = mock_exec

    result = requisitions.update_item_type_in_db(mock_session, item_type_data)
    assert result == mock_item_type
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(mock_item_type)

def test_delete_item_type_from_db_success(mock_session):
    mock_item_type = MagicMock(spec=ItemTypes)
    mock_exec = MagicMock()
    mock_exec.first.return_value = mock_item_type
    mock_session.exec.return_value = mock_exec
    result = requisitions.delete_item_type_from_db(mock_session, 1)
    mock_session.delete.assert_called_once_with(mock_item_type)
    mock_session.commit.assert_called_once()
    assert "deleted successfully" in result

def test_delete_item_type_from_db_not_found(mock_session):
    mock_exec = MagicMock()
    mock_exec.first.return_value = None
    mock_session.exec.return_value = mock_exec
    with pytest.raises(ValueError):
        requisitions.delete_item_type_from_db(mock_session, 1)

def test_add_item_brand_to_db_success(mock_session):
    item_brand = MagicMock()
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None
    result = requisitions.add_item_brand_to_db(mock_session, item_brand)
    mock_session.add.assert_called_once_with(item_brand)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(item_brand)
    assert result == item_brand

def test_add_item_brand_to_db_integrity_error(mock_session):
    item_brand = MagicMock()
    mock_session.add.side_effect = IntegrityError('statement', 'params', Exception('orig'))
    with pytest.raises(IntegrityError):
        requisitions.add_item_brand_to_db(mock_session, item_brand)
    mock_session.rollback.assert_called_once()

def test_get_item_brand_by_id_success(mock_session):
    mock_item_brand = MagicMock()
    mock_exec = MagicMock()
    mock_exec.first.return_value = mock_item_brand
    mock_session.exec.return_value = mock_exec
    result = requisitions.get_item_brand_by_id(mock_session, 1)
    assert result == mock_item_brand
    mock_session.exec.assert_called_once()

def test_get_item_brand_list_from_db_success(mock_session):
    mock_item_brand1 = MagicMock()
    mock_item_brand2 = MagicMock()
    mock_exec = MagicMock()
    mock_exec.all.return_value = [mock_item_brand1, mock_item_brand2]
    mock_session.exec.return_value = mock_exec
    result = requisitions.get_item_brand_list_from_db(mock_session)
    assert result == [mock_item_brand1, mock_item_brand2]
    mock_session.exec.assert_called_once()

def test_update_item_brand_in_db_not_found(mock_session):
    item_brand_data = MagicMock()
    item_brand_data.id = 1
    mock_exec = MagicMock()
    mock_exec.first.return_value = None
    mock_session.exec.return_value = mock_exec
    with pytest.raises(ValueError):
        requisitions.update_item_brand_in_db(mock_session, item_brand_data)

def test_update_item_brand_in_db_success(mock_session):
    item_brand_data = MagicMock()
    item_brand_data.id = 1
    item_brand_data.model_dump.return_value = {'id': 1, 'name': 'UpdatedBrand'}
    mock_item_brand = MagicMock()
    mock_exec = MagicMock()
    mock_exec.first.return_value = mock_item_brand
    mock_session.exec.return_value = mock_exec
    result = requisitions.update_item_brand_in_db(mock_session, item_brand_data)
    assert result == mock_item_brand
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(mock_item_brand)

def test_delete_item_brand_from_db_success(mock_session):
    mock_item_brand = MagicMock()
    mock_exec = MagicMock()
    mock_exec.first.return_value = mock_item_brand
    mock_session.exec.return_value = mock_exec
    result = requisitions.delete_item_brand_from_db(mock_session, 1)
    mock_session.delete.assert_called_once_with(mock_item_brand)
    mock_session.commit.assert_called_once()
    assert "deleted successfully" in result

def test_delete_item_brand_from_db_not_found(mock_session):
    mock_exec = MagicMock()
    mock_exec.first.return_value = None
    mock_session.exec.return_value = mock_exec
    with pytest.raises(ValueError):
        requisitions.delete_item_brand_from_db(mock_session, 1)

def test_create_item_in_db_success(mock_session):
    item = MagicMock()
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None
    result = requisitions.create_item_in_db(mock_session, item)
    mock_session.add.assert_called_once_with(item)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(item)
    assert result == item

def test_create_item_in_db_integrity_error(mock_session):
    item = MagicMock()
    mock_session.add.side_effect = IntegrityError('statement', 'params', Exception('orig'))
    with pytest.raises(IntegrityError):
        requisitions.create_item_in_db(mock_session, item)
    mock_session.rollback.assert_called_once()

def test_get_item_by_id_success(mock_session):
    mock_item = MagicMock()
    mock_exec = MagicMock()
    mock_exec.first.return_value = mock_item
    mock_session.exec.return_value = mock_exec
    result = requisitions.get_item_by_id(mock_session, 1)
    assert result == mock_item
    mock_session.exec.assert_called_once()

def test_get_item_list_from_db_success(mock_session):
    mock_item1 = MagicMock()
    mock_item2 = MagicMock()
    mock_exec = MagicMock()
    mock_exec.all.return_value = [mock_item1, mock_item2]
    mock_session.exec.return_value = mock_exec
    result = requisitions.get_item_list_from_db(mock_session)
    assert result == [mock_item1, mock_item2]
    mock_session.exec.assert_called_once()

def test_update_item_in_db_success(mock_session):
    updated_item = MagicMock()
    updated_item.id = 1
    updated_item.model_dump.return_value = {'id': 1, 'name': 'UpdatedItem'}
    mock_existing_item = MagicMock()
    mock_exec = MagicMock()
    mock_exec.first.return_value = mock_existing_item
    mock_session.exec.return_value = mock_exec
    result = requisitions.update_item_in_db(mock_session, updated_item)
    assert result == mock_existing_item
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(mock_existing_item)

def test_update_item_in_db_not_found(mock_session):
    updated_item = MagicMock()
    updated_item.id = 1
    mock_exec = MagicMock()
    mock_exec.first.return_value = None
    mock_session.exec.return_value = mock_exec
    with pytest.raises(ValueError):
        requisitions.update_item_in_db(mock_session, updated_item)

def test_delete_item_from_db_success(mock_session):
    mock_item = MagicMock()
    mock_exec = MagicMock()
    mock_exec.first.return_value = mock_item
    mock_session.exec.return_value = mock_exec
    result = requisitions.delete_item_from_db(mock_session, 1)
    mock_session.delete.assert_called_once_with(mock_item)
    mock_session.commit.assert_called_once()
    assert "deleted successfully" in result

def test_delete_item_from_db_not_found(mock_session):
    mock_exec = MagicMock()
    mock_exec.first.return_value = None
    mock_session.exec.return_value = mock_exec
    with pytest.raises(ValueError):
        requisitions.delete_item_from_db(mock_session, 1)

def test_create_requisition_in_db_success(mock_session):
    user_id = 1
    req_data = MagicMock()
    req_data.item_id = 10
    req_data.model_dump.return_value = {'item_id': 10}
    mock_item = MagicMock()
    mock_requisition = MagicMock()
    # Patch get_item_by_id and Requisitions
    with patch('src.db_queries.requisitions.get_item_by_id', return_value=mock_item), \
         patch('src.db_queries.requisitions.Requisitions', return_value=mock_requisition):
        result = requisitions.create_requisition_in_db(mock_session, user_id, [req_data])
        mock_session.add.assert_called_once_with(mock_requisition)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_requisition)
        assert result == [mock_requisition]

def test_create_requisition_in_db_item_not_found(mock_session):
    user_id = 1
    req_data = MagicMock()
    req_data.item_id = 10
    req_data.model_dump.return_value = {'item_id': 10}
    with patch('src.db_queries.requisitions.get_item_by_id', return_value=None):
        with pytest.raises(ValueError):
            requisitions.create_requisition_in_db(mock_session, user_id, [req_data])
        mock_session.rollback.assert_called_once()

def test_get_requisition_by_id_success(mock_session):
    mock_requisition = MagicMock()
    mock_exec = MagicMock()
    mock_exec.first.return_value = mock_requisition
    mock_session.exec.return_value = mock_exec
    result = requisitions.get_requisition_by_id(mock_session, 1)
    assert result == mock_requisition
    mock_session.exec.assert_called_once()

def test_get_all_requisitions_success(mock_session):
    mock_requisition1 = MagicMock()
    mock_requisition2 = MagicMock()
    mock_exec = MagicMock()
    mock_exec.all.return_value = [mock_requisition1, mock_requisition2]
    mock_session.exec.return_value = mock_exec
    result = requisitions.get_all_requisitions(mock_session)
    assert result == [mock_requisition1, mock_requisition2]
    mock_session.exec.assert_called_once()

def test_update_requisition_in_db_success(mock_session):
    req_id = 1
    req_data = MagicMock()
    req_data.model_dump.return_value = {'id': 1, 'item_id': 10}
    mock_requisition = MagicMock()
    mock_exec = MagicMock()
    mock_exec.first.return_value = mock_requisition
    mock_session.exec.return_value = mock_exec
    result = requisitions.update_requisition_in_db(mock_session, req_id, req_data)
    assert result == mock_requisition
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(mock_requisition)

def test_update_requisition_in_db_not_found(mock_session):
    req_id = 1
    req_data = MagicMock()
    mock_exec = MagicMock()
    mock_exec.first.return_value = None
    mock_session.exec.return_value = mock_exec
    with pytest.raises(ValueError):
        requisitions.update_requisition_in_db(mock_session, req_id, req_data)

def test_delete_requisition_from_db_success(mock_session):
    mock_requisition = MagicMock()
    mock_exec = MagicMock()
    mock_exec.first.return_value = mock_requisition
    mock_session.exec.return_value = mock_exec
    result = requisitions.delete_requisition_from_db(mock_session, 1)
    mock_session.delete.assert_called_once_with(mock_requisition)
    mock_session.commit.assert_called_once()
    assert "deleted successfully" in result

def test_delete_requisition_from_db_not_found(mock_session):
    mock_exec = MagicMock()
    mock_exec.first.return_value = None
    mock_session.exec.return_value = mock_exec
    with pytest.raises(ValueError):
        requisitions.delete_requisition_from_db(mock_session, 1)

def test_approve_requisition_in_db_success(mock_session):
    req_id = 1
    user_id = 2
    mock_requisition = MagicMock()
    mock_exec = MagicMock()
    mock_exec.first.return_value = mock_requisition
    mock_session.exec.return_value = mock_exec
    result = requisitions.approve_requisition_in_db(mock_session, req_id, user_id)
    assert result == mock_requisition
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(mock_requisition)

def test_approve_requisition_in_db_not_found(mock_session):
    req_id = 1
    user_id = 2
    mock_exec = MagicMock()
    mock_exec.first.return_value = None
    mock_session.exec.return_value = mock_exec
    with pytest.raises(ValueError):
        requisitions.approve_requisition_in_db(mock_session, req_id, user_id)

def test_deliver_requisition_in_db_success(mock_session):
    req_id = 1
    user_id = 2
    mock_requisition = MagicMock()
    mock_exec = MagicMock()
    mock_exec.first.return_value = mock_requisition
    mock_session.exec.return_value = mock_exec
    result = requisitions.deliver_requisition_in_db(mock_session, req_id, user_id)
    assert result == mock_requisition
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(mock_requisition)

def test_deliver_requisition_in_db_not_found(mock_session):
    req_id = 1
    user_id = 2
    mock_exec = MagicMock()
    mock_exec.first.return_value = None
    mock_session.exec.return_value = mock_exec
    with pytest.raises(ValueError):
        requisitions.deliver_requisition_in_db(mock_session, req_id, user_id)
