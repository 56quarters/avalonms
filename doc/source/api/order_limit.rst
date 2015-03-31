
.. Fragment for order/limit/offset params common to all informational endpoints

============= ============= ============= ============= ===============================================================
Name          Required?     Type          Mutiple?      Description
============= ============= ============= ============= ===============================================================
``limit``     No            ``integer``   No            If there are more than ``limit`` results, only ``limit`` will
                                                        be returned. This must be a positive ``integer``. If the
                                                        ``offset`` parameter is present, the ``limit`` will be applied
                                                        after the ``offset``. If the ``limit`` is not an integer
                                                        error code ``101`` (invalid parameter type) will be returned.
                                                        If the ``limit`` is not positive error code ``102`` (invalid
                                                        parameter value) will be returned.
------------- ------------- ------------- ------------- ---------------------------------------------------------------
``offset``    No            ``integer``   No            Skip the first ``offset`` entries returned as part of a result
                                                        set. This must be a positive ``integer``. This parameter does
                                                        not have any effect if the ``limit`` parameter is not also
                                                        present. If the ``offset`` is not an integer error code
                                                        ``101`` (invalid parameter type) will be returned.
------------- ------------- ------------- ------------- ---------------------------------------------------------------
``order``     No            ``string``    No            Name of the field to use for ordering the result set. Any valid
                                                        field of the members of the result set may be used. If the
                                                        ``order`` is not a valid field error code ``100`` (invalid
                                                        parameter name) will be returned.
------------- ------------- ------------- ------------- ---------------------------------------------------------------
``direction`` No            ``string``    No            Direction to sort the results in. Valid values are ``asc`` or
                                                        ``desc``. This parameter does not have any effect if the
                                                        ``order`` parameter is not also present. If the ``direction``
                                                        is not ``asc`` or ``desc`` error code ``102`` (invalid
                                                        parameter value) will be returned.
============= ============= ============= ============= ===============================================================

