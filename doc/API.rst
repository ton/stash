Stash API
=========

The stash API exposes the functionality that is used by the stash command-line
tool to interact with the stash.

:py:class:`~stash.stash.Stash` -- Class providing all operations on the stash
-----------------------------------------------------------------------------

.. autoclass:: stash.stash.Stash
    :members:

:py:class:`~stash.exception.StashException` -- Base exception class for stash exceptions
----------------------------------------------------------------------------------------

.. autoclass:: stash.exception.StashException
    :members:

:py:class:`~stash.repository.Repository` -- Interface for implementations of repository operations
--------------------------------------------------------------------------------------------------

.. autoclass:: stash.repository.Repository
    :members:

:py:class:`~stash.repository.MercurialRepository` -- Wrapper for baisc operations on Mercurial repositories
-----------------------------------------------------------------------------------------------------------

.. autoclass:: stash.repository.MercurialRepository
    :members:
