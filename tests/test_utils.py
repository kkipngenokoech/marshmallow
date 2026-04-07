import datetime as dt
import pytest

from marshmallow import utils
from marshmallow.constants import missing


class TestGetValue:
    def test_get_value_from_dict(self):
        d = {"foo": 42}
        assert utils.get_value(d, "foo") == 42
        assert utils.get_value(d, "bar", default="baz") == "baz"

    def test_get_value_from_list(self):
        lst = ["foo", "bar"]
        assert utils.get_value(lst, 0) == "foo"
        assert utils.get_value(lst, 1) == "bar"
        assert utils.get_value(lst, 2, default="baz") == "baz"

    def test_get_value_from_object(self):
        class Obj:
            foo = 42

        obj = Obj()
        assert utils.get_value(obj, "foo") == 42
        assert utils.get_value(obj, "bar", default="baz") == "baz"

    def test_get_value_nested(self):
        d = {"foo": {"bar": 42}}
        assert utils.get_value(d, "foo.bar") == 42
        assert utils.get_value(d, "foo.baz", default="qux") == "qux"

    def test_get_value_out_of_range_int_index_list(self):
        """Test that out-of-range int index on list returns default value."""
        lst = [0, 1, 2, 3, 4, 5]
        result = utils.get_value(lst, 999, default=3)
        assert result == 3

    def test_get_value_missing_int_key_dict(self):
        """Test that missing int key in dict returns default value."""
        dictionary = {1: 'a', 2: 'b', 3: 'c'}
        result = utils.get_value(dictionary, 4, default='z')
        assert result == 'z'

    def test_get_value_out_of_range_int_index_list_of_objects(self):
        """Test that out-of-range int index on list of objects returns default value."""
        class PointClass:
            def __init__(self, x, y):
                self.x = x
                self.y = y

        list_obj = [[PointClass(24, 42), {"x": 24, "y": 42}]]
        result = utils.get_value(list_obj, 3, default=None)
        assert result is None

    def test_get_value_negative_int_index(self):
        """Test that negative int index works correctly."""
        lst = [0, 1, 2, 3, 4, 5]
        result = utils.get_value(lst, -1, default="default")
        assert result == 5
        
        # Test out-of-range negative index
        result = utils.get_value(lst, -10, default="default")
        assert result == "default"

    def test_get_value_int_key_on_object_without_getitem(self):
        """Test that int key on object without __getitem__ returns default."""
        class SimpleObj:
            pass
        
        obj = SimpleObj()
        result = utils.get_value(obj, 42, default="default")
        assert result == "default"


class TestSetValue:
    def test_set_value_simple(self):
        d = {}
        utils.set_value(d, "foo", 42)
        assert d == {"foo": 42}

    def test_set_value_nested(self):
        d = {}
        utils.set_value(d, "foo.bar", 42)
        assert d == {"foo": {"bar": 42}}

    def test_set_value_nested_existing(self):
        d = {"foo": {"baz": 24}}
        utils.set_value(d, "foo.bar", 42)
        assert d == {"foo": {"baz": 24, "bar": 42}}

    def test_set_value_nested_conflict(self):
        d = {"foo": "bar"}
        with pytest.raises(ValueError, match="Cannot set foo.bar in foo"):
            utils.set_value(d, "foo.bar", 42)


class TestPluck:
    def test_pluck(self):
        dlist = [{"id": 1, "name": "foo"}, {"id": 2, "name": "bar"}]
        result = utils.pluck(dlist, "id")
        assert result == [1, 2]


class TestIsGenerator:
    def test_is_generator_function(self):
        def gen():
            yield 1

        assert utils.is_generator(gen) is True

    def test_is_generator_object(self):
        def gen():
            yield 1

        g = gen()
        assert utils.is_generator(g) is True

    def test_is_not_generator(self):
        assert utils.is_generator(42) is False
        assert utils.is_generator([1, 2, 3]) is False


class TestIsIterableButNotString:
    def test_is_iterable_but_not_string(self):
        assert utils.is_iterable_but_not_string([1, 2, 3]) is True
        assert utils.is_iterable_but_not_string((1, 2, 3)) is True
        assert utils.is_iterable_but_not_string({1, 2, 3}) is True
        assert utils.is_iterable_but_not_string({"a": 1}) is True

    def test_is_not_iterable_but_not_string(self):
        assert utils.is_iterable_but_not_string("string") is False
        assert utils.is_iterable_but_not_string(b"bytes") is False
        assert utils.is_iterable_but_not_string(42) is False


class TestIsSequenceButNotString:
    def test_is_sequence_but_not_string(self):
        assert utils.is_sequence_but_not_string([1, 2, 3]) is True
        assert utils.is_sequence_but_not_string((1, 2, 3)) is True

    def test_is_not_sequence_but_not_string(self):
        assert utils.is_sequence_but_not_string("string") is False
        assert utils.is_sequence_but_not_string(b"bytes") is False
        assert utils.is_sequence_but_not_string({1, 2, 3}) is False
        assert utils.is_sequence_but_not_string({"a": 1}) is False
        assert utils.is_sequence_but_not_string(42) is False


class TestIsCollection:
    def test_is_collection(self):
        assert utils.is_collection([1, 2, 3]) is True
        assert utils.is_collection((1, 2, 3)) is True
        assert utils.is_collection({1, 2, 3}) is True

    def test_is_not_collection(self):
        assert utils.is_collection("string") is False
        assert utils.is_collection(b"bytes") is False
        assert utils.is_collection({"a": 1}) is False
        assert utils.is_collection(42) is False


class TestIsAware:
    def test_is_aware(self):
        aware_dt = dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc)
        assert utils.is_aware(aware_dt) is True

    def test_is_not_aware(self):
        naive_dt = dt.datetime(2023, 1, 1)
        assert utils.is_aware(naive_dt) is False


class TestFromTimestamp:
    def test_from_timestamp(self):
        timestamp = 1672531200.0  # 2023-01-01 00:00:00 UTC
        result = utils.from_timestamp(timestamp)
        expected = dt.datetime(2023, 1, 1, 0, 0, 0)
        assert result == expected
        assert result.tzinfo is None

    def test_from_timestamp_invalid(self):
        with pytest.raises(ValueError, match="Not a valid POSIX timestamp"):
            utils.from_timestamp(True)
        with pytest.raises(ValueError, match="Not a valid POSIX timestamp"):
            utils.from_timestamp(False)
        with pytest.raises(ValueError, match="Not a valid POSIX timestamp"):
            utils.from_timestamp(-1)

    def test_from_timestamp_overflow(self):
        with pytest.raises(ValueError, match="Timestamp is too large"):
            utils.from_timestamp(1e20)


class TestFromTimestampMs:
    def test_from_timestamp_ms(self):
        timestamp_ms = 1672531200000  # 2023-01-01 00:00:00 UTC in milliseconds
        result = utils.from_timestamp_ms(timestamp_ms)
        expected = dt.datetime(2023, 1, 1, 0, 0, 0)
        assert result == expected
        assert result.tzinfo is None

    def test_from_timestamp_ms_invalid(self):
        with pytest.raises(ValueError, match="Not a valid POSIX timestamp"):
            utils.from_timestamp_ms(True)
        with pytest.raises(ValueError, match="Not a valid POSIX timestamp"):
            utils.from_timestamp_ms(False)


class TestTimestamp:
    def test_timestamp_aware(self):
        aware_dt = dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc)
        result = utils.timestamp(aware_dt)
        assert result == 1672531200.0

    def test_timestamp_naive(self):
        naive_dt = dt.datetime(2023, 1, 1)
        result = utils.timestamp(naive_dt)
        assert result == 1672531200.0


class TestTimestampMs:
    def test_timestamp_ms(self):
        aware_dt = dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc)
        result = utils.timestamp_ms(aware_dt)
        assert result == 1672531200000.0


class TestEnsureTextType:
    def test_ensure_text_type_string(self):
        result = utils.ensure_text_type("hello")
        assert result == "hello"
        assert isinstance(result, str)

    def test_ensure_text_type_bytes(self):
        result = utils.ensure_text_type(b"hello")
        assert result == "hello"
        assert isinstance(result, str)


class TestCallableOrRaise:
    def test_callable_or_raise_callable(self):
        def func():
            pass

        result = utils.callable_or_raise(func)
        assert result is func

    def test_callable_or_raise_not_callable(self):
        with pytest.raises(TypeError, match="Object 42 is not callable"):
            utils.callable_or_raise(42)


class TestTimedeltaToMicroseconds:
    def test_timedelta_to_microseconds(self):
        td = dt.timedelta(days=1, seconds=3661, microseconds=123456)
        result = utils.timedelta_to_microseconds(td)
        expected = (1 * 24 * 3600 + 3661) * 1000000 + 123456
        assert result == expected

    def test_timedelta_to_microseconds_zero(self):
        td = dt.timedelta()
        result = utils.timedelta_to_microseconds(td)
        assert result == 0
