
.. Fragment for order/limit/offset params common to all informational endpoints

* ``limit``

  + Type: ``integer``

  + Description: If there are more than ``limit`` results, only ``limit`` will
    be returned. This must be a positive ``integer``. If the ``offset`` parameter
    is present, the ``limit`` will be applied after the ``offset``.

* ``offset``

  + Type: ``integer``

  + Description: Skip the first ``offset`` entries returned as part of a result
    set. This must be a positive ``integer``. This parameter does not have any
    effect if the ``limit`` parameter is not also present.

* ``order``

  + Type: ``string``

  + Description: Name of the field to use for ordering the result set. Any valid
    field of the members of the result set may be used.

* ``direction``

  + Type: ``string``

  + Description: Direction to sort the results in. Valid values are ``asc`` or
    ``desc``. This parameter does not have any effect if the ``order`` parameter
    is not also present.
