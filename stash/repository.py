import inspect
import os
import subprocess
import sys

from abc import ABCMeta, abstractmethod

from .exception import StashException

class FileStatus(object):
    """Enum for all possible file states that are handled by stash."""
    Added, Removed = range(2)

class Repository(object):
    """Abstract class that defines an interface for all functionality required
    by :py:class:`~stash.stash.Stash` to properly interface with a version
    control system.
    """
    __metaclass__ = ABCMeta

    def __init__(self, path, create=False):
        """Creating a concrete repository instance is done using the factory
        method :py:meth:`~stash.repository.Repository.__new__`. After the
        factory has created a class instance, the repository is initialized by
        specifying a *path* within the repository.
        """

        self.root_path = self.get_root_path(path)
        """Root path of the repository."""

        # In case no valid repository could be found, and one should be created,
        # do so.
        if create and self.root_path is None:
            # In case the repository path does not yet exist, create it first.
            if not os.path.exists(path):
                os.mkdir(path)

            # Make sure that the root path of the repository points to the
            # specified root path.
            self.root_path = os.path.abspath(path)

            # Finally, create the repository.
            self.init()

        super(Repository, self).__init__(self)

    def __new__(cls, path, create=False):
        """Factory that will return the right repository wrapper depending on
        the repository type that is detected for *path*.

        :raises: :py:exc:`~stash.exception.StashException` in case no repository is
            found at *path*.
        """
        # Iterate over all repository implementations, and for each
        # implementation, determine whether it can find a root path for the
        # repository specified at the specified path.
        if cls == Repository:
            for name, repository_cls in inspect.getmembers(sys.modules[cls.__module__]):
                if inspect.isclass(repository_cls) and Repository in repository_cls.__bases__:
                    repository_root = repository_cls.get_root_path(path)
                    if repository_root is not None:
                        # A root path for the current repository implementation
                        # could be found, create an instance of this class.
                        return super(Repository, repository_cls).__new__(repository_cls)

            raise StashException("no valid repository found at '%s'" % path)
        else:
            return super(Repository, cls).__new__(cls, path, create)

    def _execute(self, command, stdin=None, stdout=subprocess.PIPE):
        """Executes the specified command relative to the repository root.
        Returns a tuple containing the return code and the process output.
        """
        process = subprocess.Popen(command, shell=True, cwd=self.root_path, stdin=stdin, stdout=stdout)
        return (process.wait(), None if stdout is not subprocess.PIPE else process.communicate()[0].decode('utf-8'))

    @abstractmethod
    def add(self, file_names):
        """Adds all files in *file_names* to the repository."""
        pass

    def apply_patch(self, patch_path):
        """Applies the patch located at *patch_path*. Returns the return code of
        the patch command.
        """
        # Do not create .orig backup files, and merge files in place.
        return self._execute('patch -p1 --no-backup-if-mismatch --merge', stdout=open(os.devnull, 'w'), stdin=open(patch_path, 'r'))[0]

    @abstractmethod
    def commit(self, message):
        """Commits all changes in the repository with the specified commit
        *message*.
        """
        pass

    @abstractmethod
    def diff(self):
        """Returns a diff text for all changes in the repository."""
        pass

    @abstractmethod
    def init(self, path):
        """Creates a repository at the specified *path*."""
        pass

    @abstractmethod
    def remove(self, file_names):
        """Removes all files in *file_names* from the repository."""
        pass

    @abstractmethod
    def revert_all(self):
        """Reverts all changes in a repository without creating any backup
        files.
        """
        pass

    @classmethod
    @abstractmethod
    def get_root_path(cls, path):
        """Returns the root path for the repository location *path*. In case
        *path* is not part of a repository, `None` is returned.
        """
        pass

    @abstractmethod
    def status(self):
        """Returns the current status of all files in the repository."""
        pass

class MercurialRepository(Repository):
    """Concrete implementation of :py:class:`~stash.repository.Repository` for
    Mercurial repositories.
    """

    def add(self, file_names):
        """See :py:meth:`~stash.repository.Repository.add`."""
        self._execute('hg add %s' % (' '.join(file_names)))

    def commit(self, message):
        """See :py:meth:`~stash.repository.Repository.commit`."""
        self._execute('hg ci -m "%s" -u anonymous' % message)

    def diff(self):
        """See :py:meth:`~stash.repository.Repository.diff`."""
        return self._execute('hg diff -a')[1]

    def init(self):
        """See :py:meth:`~stash.repository.Repository.init`."""
        self._execute('hg init')

    def remove(self, file_names):
        """See :py:meth:`~stash.repository.Repository.remove`."""
        self._execute('hg rm %s' % (' '.join(file_names)))

    def revert_all(self):
        """See :py:meth:`~stash.repository.Repository.revert_all`."""
        self._execute('hg revert -q -C --all')

    @classmethod
    def get_root_path(self, path):
        """See :py:meth:`~stash.repository.Repository.get_root_path`."""
        # Look at the directories present in the current working directory. In case
        # a .hg directory is present, we know we are in the root directory of a
        # Mercurial repository. In case no repository specific folder is found, and
        # the current directory has a parent directory, look if a repository
        # specific directory can be found in the parent directory.
        while path != '/':
            if '.hg' in os.listdir(path):
                return path
            path = os.path.abspath(os.path.join(path, os.pardir))

        # No Mercurial repository found.
        return None

    def status(self):
        """See :py:meth:`~stash.repository.Repository.status`."""
        result = set()
        for line in self._execute('hg stat')[1].splitlines():
            if line[0] == '?':
                result.add((FileStatus.Added, line[2:].strip()))
            elif line[0] == '!':
                result.add((FileStatus.Removed, line[2:].strip()))
        return result

class SubversionRepository(Repository):
    """Concrete implementation of :py:class:`~stash.repository.Repository` for
    Subversion repositories.
    """

    def add(self, file_names):
        """See :py:meth:`~stash.repository.Repository.add`."""
        self._execute('svn add --parents %s' % (' '.join(file_names)))

    def commit(self, message):
        """See :py:meth:`~stash.repository.Repository.commit`."""
        self._execute('svn ci -m "%s" --username anonymous' % message)

    def diff(self):
        """See :py:meth:`~stash.repository.Repository.diff`."""
        return self._execute('svn diff --git')[1]

    def init(self):
        """See :py:meth:`~stash.repository.Repository.init`."""
        self._execute('svnadmin create --fs-type fsfs .svn-db')
        self._execute('svn co file://%s/.svn-db .' % self.root_path)

    def remove(self, file_names):
        """See :py:meth:`~stash.repository.Repository.remove`."""
        self._execute('svn rm %s' % (' '.join(file_names)))

    def revert_all(self):
        """See :py:meth:`~stash.repository.Repository.revert_all`."""
        self._execute('svn revert -R -q .')

    @classmethod
    def get_root_path(self, path):
        """See :py:meth:`~stash.repository.Repository.get_root_path`."""
        # Look at the directories present in the current working directory. In
        # case a .svn directory is present, we know we are in the root directory
        # of a Subversion repository (for Subversion 1.7.x). In case no
        # repository specific folder is found, and the current directory has a
        # parent directory, look if a repository specific directory can be found
        # in the parent directory.
        while path != '/':
            if '.svn' in os.listdir(path):
                return path
            path = os.path.abspath(os.path.join(path, os.pardir))

        # No Subversion repository found.
        return None

    def status(self):
        """See :py:meth:`~stash.repository.Repository.status`."""
        result = set()
        for line in self._execute('svn stat')[1].splitlines():
            if line[0] == '?':
                result.add((FileStatus.Added, line[2:].strip()))
            elif line[0] == '!':
                result.add((FileStatus.Removed, line[2:].strip()))
        return result
