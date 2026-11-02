/*

    Scalar Traj Interface Class
    This class is a general interface to scalar trajectory generators classes

    Copyright 2019-2020 Università della Campania Luigi Vanvitelli

    Author: Marco Costanzo <marco.costanzo@unicampania.it>

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

#ifndef SCALAR_TRAJ_INTERFACE_H
#define SCALAR_TRAJ_INTERFACE_H

#include "sun_traj_lib/Traj_Generator_Interface.h"

namespace sun
{
//! Abstract class representing a Scalar traj
class Scalar_Traj_Interface : public Traj_Generator_Interface
{
private:
  /*!
      No default Constructor
  */
  Scalar_Traj_Interface();

public:
  /*====== CONSTRUCTORS =========*/

  /*!
      Constructor with duration and initial time as input
  */
  Scalar_Traj_Interface(double duration, double initial_time = 0.0) : Traj_Generator_Interface(duration, initial_time)
  {
  }

  /*!
      Clone the object in the heap
  */
  virtual Scalar_Traj_Interface* clone() const = 0;

  /*====== END CONSTRUCTORS =========*/

  /*====== RUNNERS =========*/

  /*!
      Get Position at time secs
  */
  virtual double getPosition(double secs) const = 0;

  /*!
      Get Velocity at time secs
  */
  virtual double getVelocity(double secs) const = 0;

  /*!
      Get Acceleration at time secs
  */
  virtual double getAcceleration(double secs) const = 0;

  /*====== END RUNNERS =========*/

};  // END CLASS Scalar_Traj_Interface

using Scalar_Traj_Interface_Ptr = std::unique_ptr<Scalar_Traj_Interface>;

}  // namespace sun

#endif