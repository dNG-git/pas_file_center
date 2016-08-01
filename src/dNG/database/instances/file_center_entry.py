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
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;gpl
----------------------------------------------------------------------------
#echo(pasFileCenterVersion)#
#echo(__FILEPATH__)#
"""

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import BIGINT, BOOLEAN, CHAR, INT, TEXT, VARCHAR

from .data_linker import DataLinker
from .ownable_mixin import OwnableMixin

class FileCenterEntry(DataLinker, OwnableMixin):
#
	"""
"FileCenterEntry" represents an database file center entry.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: file_center
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	__tablename__ = "{0}_file_center_entry".format(DataLinker.get_table_prefix())
	"""
SQLAlchemy table name
	"""
	db_instance_class = "dNG.data.file_center.Entry"
	"""
Encapsulating SQLAlchemy database instance class name
	"""
	db_schema_version = 1
	"""
Database schema version
	"""

	id = Column(VARCHAR(32), ForeignKey(DataLinker.id), primary_key = True)
	"""
file_center_entry.id
	"""
	vfs_url = Column(TEXT, index = True)
	"""
file_center_entry.vfs_url
	"""
	vfs_type = Column(INT, index = True, server_default = "0", nullable = False)
	"""
file_center_entry.mimeclass
	"""
	role_id = Column(VARCHAR(100), index = True)
	"""
file_center_entry.role_id
	"""
	owner_type = Column(CHAR(1), server_default = "u", nullable = False)
	"""
file_center_entry.owner_type
	"""
	owner_id = Column(VARCHAR(32))
	"""
file_center_entry.owner_id
	"""
	owner_ip = Column(VARCHAR(100))
	"""
file_center_entry.owner_ip
	"""
	mimeclass = Column(VARCHAR(100), index = True, server_default = "unknown", nullable = False)
	"""
file_center_entry.mimeclass
	"""
	mimetype = Column(VARCHAR(255), index = True, server_default = "application/octet-stream", nullable = False)
	"""
file_center_entry.mimetype
	"""
	size = Column(BIGINT, server_default = "0", nullable = False)
	"""
file_center_entry.size
	"""
	locked = Column(BOOLEAN, server_default = "0", nullable = False)
	"""
file_center_entry.locked
	"""
	guest_permission = Column(CHAR(1), server_default = "", nullable = False)
	"""
file_center_entry.guest_permission
	"""
	user_permission = Column(CHAR(1), server_default = "", nullable = False)
	"""
file_center_entry.user_permission
	"""

	__mapper_args__ = { "polymorphic_identity": "FileCenterEntry" }
	"""
sqlalchemy.org: Other options are passed to mapper() using the
__mapper_args__ class variable.
	"""
#

##j## EOF