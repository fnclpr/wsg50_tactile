/*

    Quaternion Trajectory Generator Class
    This class is an interface to generate arbitrary UnitQuaternion trajectory in the cartesian space

    Copyright 2018-2020 Università della Campania Luigi Vanvitelli

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

#ifndef QUATERNION_TRAJ_INTERFACE_H
#define QUATERNION_TRAJ_INTERFACE_H

#include "TooN/TooN.h"
#include "sun_math_toolbox/UnitQuaternion.h"
#include "sun_traj_lib/Traj_Generator_Interface.h"

namespace sun
{
//! Abstract class representing a rotatin traj (UnitQuaternion)
class Quaternion_Traj_Interface : public Traj_Generator_Interface
{
private:
  /*!
      Avoid Default constructor
  */
  Quaternion_Traj_Interface();

protected:
  TooN::Vector<3, int> _mask;

public:
  /*======CONSTRUCTORS=========*/

  /*!
      Constructor with total time as input
  */
  Quaternion_Traj_Interface(double duration, double initial_time = 0.0)
    : Traj_Generator_Interface(duration, initial_time)
  {
  }

  /*!
      Clone the object in the heap
  */
  virtual Quaternion_Traj_Interface* clone() const = 0;

  // Quaternion_Traj_Interface( const Quaternion_Traj_Interface& traj );

  /*======END CONSTRUCTORS=========*/

  /*====== GETTERS =========*/

  /*!
      Get the mask at time secs, if mask[i]=0 then the i-th cartesian coordinate should not be taken into account
      Warning: these are UnitQuaternion !!
  */
  virtual TooN::Vector<3, int> getMask(double secs) const
  {
    return _mask;
  }

  /*====== END GETTERS =========*/

  /*====== SETTERS =========*/

  /*!
      Set the mask at time secs, if mask[i]=0 then the i-th cartesian coordinate should not be taken into account
      Warning: these are UnitQuaternion !!
  */
  virtual void setMask(TooN::Vector<3, int> mask)
  {
    _mask = mask;
  }

  /*====== END SETTERS =========*/

  /*====== TRANSFORM =========*/

  /*!
      Change the reference frame of the trajectory
      Apply an homogeneous transfrmation matrix to the trajectory
      new_T_curr is the homog transf matrix of the current frame w.r.t. the new frame
  */
  virtual void changeFrame(const TooN::Matrix<4, 4>& new_T_curr)
  {
    changeFrame(t2r(new_T_curr));
  }

  /*!
      Change the reference frame of the trajectory
      Apply a rotation matrix to the trajectory
      new_R_curr is the rotation matrix of the current frame w.r.t. the new frame
  */
  virtual void changeFrame(const TooN::Matrix<3, 3>& new_R_curr)
  {
    std::cout << TRAJ_ERROR_COLOR "Error in Quaterion_Traj_Interface::changeFrame( TooN::Matrix<4,4> new_T_curr ) | "
                                  "Not implemented..." CRESET
              << std::endl;
    exit(-1);
  }

  /*!
      Change the reference frame of the trajectory
      Apply a rotation matrix to the trajectory
      new_Q_curr is the Quaterion representing the rotation matrix of the current frame w.r.t. the new frame
  */
  virtual void changeFrame(const UnitQuaternion& new_Q_curr)
  {
    changeFrame(new_Q_curr.torot());
  }

  /*====== END TRANSFORM =========*/

  /*!
       Get Quaternion at time secs
  */
  virtual UnitQuaternion getQuaternion(double secs) const = 0;

  /*!
      Get Angular Velocity at time secs
  */
  virtual TooN::Vector<3> getVelocity(double secs) const = 0;

  /*!
      Get Angular Acceleration at time secs
  */
  virtual TooN::Vector<3> getAcceleration(double secs) const = 0;

};  // END CLASS Quterion_Traj_Interface

using Quaternion_Traj_Interface_Ptr = std::unique_ptr<Quaternion_Traj_Interface>;

}  // namespace sun

#endif