# -*- coding: utf-8 -*-
##j## BOF

"""
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?pas;file_center

The following license agreement remains valid unless any additions or
changes are being made by direct Netware Group in a written form.

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc.,
59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;gpl
----------------------------------------------------------------------------
#echo(pasFileCenterVersion)#
#echo(__FILEPATH__)#
"""

# pylint: disable=import-error,no-name-in-module

from dNG.data.binary import Binary
from dNG.data.data_linker import DataLinker
from dNG.data.ownable_lockable_read_mixin import OwnableLockableReadMixin
from dNG.data.ownable_mixin import OwnableMixin as OwnableInstance
from dNG.database.connection import Connection
from dNG.database.instances.file_center_entry import FileCenterEntry as _DbFileCenterEntry
from dNG.database.lockable_mixin import LockableMixin
from dNG.database.nothing_matched_exception import NothingMatchedException
from dNG.database.sort_definition import SortDefinition
from dNG.database.transaction_context import TransactionContext
from dNG.vfs.abstract import Abstract
from dNG.vfs.implementation import Implementation
from dNG.runtime.value_exception import ValueException

class Entry(DataLinker, OwnableLockableReadMixin):
#
	"""
"Entry" represents an database file center entry.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: file_center
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	VFS_TYPE_DIRECTORY = 1
	"""
VFS container type
	"""
	VFS_TYPE_ITEM = 2
	"""
VFS item type
	"""

	_DB_INSTANCE_CLASS = _DbFileCenterEntry
	"""
SQLAlchemy database instance class to initialize for new instances.
	"""

	def __init__(self, db_instance = None):
	#
		"""
Constructor __init__(Entry)

:param db_instance: Encapsulated SQLAlchemy database instance

:since: v0.1.00
		"""

		DataLinker.__init__(self, db_instance)
		LockableMixin.__init__(self)
		OwnableLockableReadMixin.__init__(self)

		self.vfs_object = None
		"""
Underlying VFS object
		"""

		self.set_max_inherited_permissions(OwnableLockableReadMixin.READABLE,
		                                   OwnableLockableReadMixin.READABLE
		                                  )
	#

	def __del__(self):
	#
		"""
Destructor __del__(Entry)

:since: v0.1.00
		"""

		self.close()
	#

	def __getattr__(self, name):
	#
		"""
python.org: Called when an attribute lookup has not found the attribute in
the usual places (i.e. it is not an instance attribute nor is it found in the
class tree for self).

:param name: Attribute name

:return: (mixed) Underlying VFS object attribute
:since:  v0.1.00
		"""

		self._ensure_vfs_object_instance()
		return getattr(self.vfs_object, name)
	#

	def close(self):
	#
		"""
python.org: Flush and close this stream.

:since: v0.1.00
		"""

		if (self.vfs_object is not None and self.vfs_object.is_valid()):
		#
			self.flush()

			try: self.vfs_object.close()
			finally: self.vfs_object = None
		#
	#

	def delete(self):
	#
		"""
Deletes this entry from the database.

:since: v0.1.00
		"""

		with self, TransactionContext():
		#
			if (self.type & Entry.VFS_TYPE_DIRECTORY == Entry.VFS_TYPE_DIRECTORY):
			#
				for entry in self.get_content_list(): entry.delete()
			#

			db_resource_metadata_instance = self.local.db_instance.rel_resource_metadata

			DataLinker.delete(self)
			if (db_resource_metadata_instance is not None): self.local.connection.delete(db_resource_metadata_instance)
		#
	#

	def _ensure_vfs_object_instance(self):
	#
		"""
Checks or creates a new instance for the stored file.

:since: v0.1.00
		"""

		if (self.vfs_object is None or (not self.vfs_object.is_valid())):
		#
			with self:
			#
				vfs_url = self.get_vfs_url()
				if (vfs_url is None): raise ValueException("VFS URL not defined")
				self.vfs_object = Implementation.load_vfs_url(vfs_url)
			#
		#
	#

	def flush(self):
	#
		"""
python.org: Flush the write buffers of the stream if applicable.

:since: v0.1.03
		"""

		if (self.vfs_object is not None and self.vfs_object.is_valid()):
		#
			if (self.vfs_object.is_supported("flush")): self.vfs_object.flush()

			entry_data = self.get_data_attributes("size")
			vfs_size = self.vfs_object.get_size()

			if (entry_data['size'] != vfs_size):
			#
				with self: self.set_data_attributes(size = vfs_size)
			#
		#
	#

	def _get_default_sort_definition(self, context = None):
	#
		"""
Returns the default sort definition list.

:param context: Sort definition context

:return: (object) Sort definition
:since:  v0.1.00
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._get_default_sort_definition({1})- (#echo(__LINE__)#)", self, context, context = "pas_datalinker")

		return (SortDefinition([ ( "position", SortDefinition.ASCENDING ),
		                         ( "vfs_type", SortDefinition.ASCENDING ),
		                         ( "title", SortDefinition.ASCENDING )
		                       ])
		        if (context == "Entry") else
		        DataLinker._get_default_sort_definition(self, context)
		       )
	#

	def get_vfs_object(self):
	#
		"""
Returns the VFS object of this file center entry.

:return: VFS object referenced by this file center entry
:since:  v0.1.00
		"""

		self._ensure_vfs_object_instance()
		return self.vfs_object
	#

	get_vfs_url = DataLinker._wrap_getter("vfs_url")
	"""
Returns the VFS URL of this instance.

:return: (str) File center entry VFS URL; None if undefined
:since:  v0.1.00
	"""

	def _insert(self):
	#
		"""
Insert the instance into the database.

:since: v0.1.00
		"""

		# pylint: disable=maybe-no-member

		DataLinker._insert(self)

		is_acl_missing = (len(self.local.db_instance.rel_acl) == 0)
		is_data_missing = self.is_data_attribute_none("owner_type")
		is_directory_mimeclass = (self.local.db_instance.mimeclass == "directory")
		is_permission_missing = self.is_data_attribute_none("guest_permission", "user_permission")

		parent_object = (self.load_parent()
		                 if (is_acl_missing or is_data_missing or is_directory_mimeclass or is_permission_missing) else
		                 None
		                )

		if (is_data_missing and isinstance(parent_object, DataLinker)):
		#
			parent_data = parent_object.get_data_attributes("id_site")
			if (self.local.db_instance.id_site is None and parent_data['id_site'] is not None): self.local.db_instance.id_site = parent_data['id_site']
		#

		if (is_directory_mimeclass and isinstance(parent_object, Entry)): self.local.db_instance.mimetype = parent_object.get_mimetype()

		if (isinstance(parent_object, OwnableInstance)):
		#
			if (is_acl_missing): self._copy_acl_entries_from_instance(parent_object)
			if (is_permission_missing): self._copy_default_permission_settings_from_instance(parent_object)
		#
	#

	def save(self):
	#
		"""
Saves changes of the database task instance.

:since: v0.1.00
		"""

		with self, self.local.connection.no_autoflush:
		#
			if (self.local.db_instance.vfs_type is None or self.local.db_instance.vfs_type == 0):
			#
				self._ensure_vfs_object_instance()

				if (self.vfs_object is None):
				#
					if (self.local.db_instance.mimeclass == "directory"): self.local.db_instance.vfs_type = Entry.VFS_TYPE_DIRECTORY
				#
				else: self.local.db_instance.vfs_type = (Entry.VFS_TYPE_DIRECTORY if (self.vfs_object.is_directory()) else Entry.VFS_TYPE_ITEM)
			#

			DataLinker.save(self)
		#
	#

	def set_data_attributes(self, **kwargs):
	#
		"""
Sets values given as keyword arguments to this method.

:since: v0.1.00
		"""

		with self, self.local.connection.no_autoflush:
		#
			DataLinker.set_data_attributes(self, **kwargs)

			if ("vfs_url" in kwargs): self.local.db_instance.vfs_url = Binary.utf8(kwargs['vfs_url'])
			if ("role_id" in kwargs): self.local.db_instance.role_id = Binary.utf8(kwargs['role_id'])
			if ("owner_type" in kwargs): self.local.db_instance.owner_type = kwargs['owner_type']
			if ("owner_id" in kwargs): self.local.db_instance.owner_id = kwargs['owner_id']
			if ("owner_ip" in kwargs): self.local.db_instance.owner_ip = kwargs['owner_ip']
			if ("mimeclass" in kwargs): self.local.db_instance.mimeclass = kwargs['mimeclass']
			if ("mimetype" in kwargs): self.local.db_instance.mimetype = kwargs['mimetype']
			if ("size" in kwargs): self.local.db_instance.size = kwargs['size']
			if ("locked" in kwargs): self.local.db_instance.locked = kwargs['locked']
			if ("guest_permission" in kwargs): self.local.db_instance.guest_permission = kwargs['guest_permission']
			if ("user_permission" in kwargs): self.local.db_instance.user_permission = kwargs['user_permission']
		#
	#

	def set_vfs_object(self, vfs_object):
	#
		"""
Sets an VFS object for this file center entry.

:param vfs_object: VFS object to be referenced by this file center entry

:since: v0.1.00
		"""

		if (not isinstance(vfs_object, Abstract)): raise ValueException("VFS object given is invalid")
		if (self.get_vfs_url() is not None): raise ValueException("Setting a VFS object is not supported if an VFS URL is already defined")

		self.set_data_attributes(title = vfs_object.get_name(),
		                         vfs_url = vfs_object.get_url(),
		                         size = vfs_object.get_size()
		                        )

		self.vfs_object = vfs_object
	#

	@classmethod
	def load_role_id(cls, _id):
	#
		"""
Load Entry instance by its role ID.

:param cls: Expected encapsulating database instance class
:param _id: Role ID

:return: (object) Entry instance on success
:since:  v0.1.00
		"""

		if (_id is None): raise NothingMatchedException("Role ID is invalid")

		with Connection.get_instance():
		#
			db_instance = DataLinker.get_db_class_query(cls).filter(_DbFileCenterEntry.role_id == _id).first()

			if (db_instance is None): raise NothingMatchedException("Role ID '{0}' is invalid".format(_id))
			DataLinker._ensure_db_class(cls, db_instance)

			return Entry(db_instance)
		#
	#

	@classmethod
	def load_vfs_url(cls, url):
	#
		"""
Load Entry instance by its VFS URL.

:param cls: Expected encapsulating database instance class
:param url: VFS URL

:return: (object) Entry instance on success
:since:  v0.1.00
		"""

		if (url is None): raise NothingMatchedException("VFS URL is invalid")

		with Connection.get_instance():
		#
			db_instance = DataLinker.get_db_class_query(cls).filter(_DbFileCenterEntry.vfs_url == url).first()

			if (db_instance is None): raise NothingMatchedException("VFS URL '{0}' is invalid".format(url))
			DataLinker._ensure_db_class(cls, db_instance)

			return Entry(db_instance)
		#
	#

	@staticmethod
	def new_stored_file():
	#
		"""
Creates a new Entry instance for a file backed by an StoredFile instance.

:return: (object) Entry instance on success
:since:  v0.1.00
		"""

		file_instance = Implementation.new_vfs_url(Implementation.TYPE_FILE, "x-file-store://")

		_return = Entry()
		_return.set_vfs_object(file_instance)

		return _return
	#
#

##j## EOF