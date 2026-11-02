/*
    Helper Functions to read ANN from file

    Copyright 2019 Università della Campania Luigi Vanvitelli

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef ANN_FILE_READER_H
#define ANN_FILE_READER_H

#include <ANN/ANN.h>
#include <ANN/ANN_PCA_Layer.h>
#include <ANN/ANN_MapMinMax.h>
#include <ANN/ANN_Fully_Connected_Layer.h>
#include <ANN/ANN_Activation_Fcns.h>

ANN readANNFile( const std::string file_path );
ANN_PCA_Layer readPCALayerFile(FILE *f);
ANN_MapMinMax readMapMinMaxLayerFile(FILE *f, bool b_reverse = false);
ANN_Fully_Connected_Layer readFullyConnectedLayerFile(FILE *f);

#endif