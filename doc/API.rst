Shelve API
==========

The shelve API exposes the functionality that is used by the shelve command-line
tool to interact with the shelf.

:py:class:`~shelf.shelf.Shelf` -- Class providing all operations on the shelf
-----------------------------------------------------------------------------

.. autoclass:: shelf.shelf.Shelf
    :members:

:py:class:`~shelf.exception.ShelfException` -- Base exception class for shelf exceptions
----------------------------------------------------------------------------------------

.. autoclass:: shelf.exception.ShelfException
    :members:

:py:class:`~shelf.repository.Repository` -- Interface for implementations of repository operations
--------------------------------------------------------------------------------------------------

.. autoclass:: shelf.repository.Repository
    :members:

:py:class:`~shelf.repository.MercurialRepository` -- Wrapper for baisc operations on Mercurial repositories
-----------------------------------------------------------------------------------------------------------

.. autoclass:: shelf.repository.MercurialRepository
    :members:
