# biodata
A biological data entry application with ajax/jquery interface written in Python and Flask

Biodata is used by [Marine Conservation Philippines](http://www.marineconservationphilippines.org) for the entry of their surveying data. It was born out of a need of recording data with many different researchers, while needing to reduce user error. For analysis and management purposes having the data in a relational database is an enormous advantage over the tranditional flat spreadsheets that are often used.

The basis for the application are the sample, site, observation and observer. On top of that it is expandable with multiple datasets each defining their own variation to this. Extra objects can be added, like for instance species could be added to an observation, and for each object, extra fields can be defined as well. The forms are all autogenerated based on the dataset definition. The form uses ajax to make the data entry as quick as possible, possibly using keyboard navigation.
Validation on the forms is done as well, and complex validation like valid ranges for number fields can be defined in the datamodel. User error is therefore reduced.

The application isn't meant for the large public as is, but works quite well for us.

Copyright (C) 2015  Dolf Andringa

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. This is included in the LICENSE file.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

