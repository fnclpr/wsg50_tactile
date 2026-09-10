/*

    Cartesian Trajectory Generator Class
    This class is an interface to generate arbitrary cartesian trajectory in the cartesian space
    the angular position is giver as UnitQuaterion

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

#ifndef CARTESIAN_TRAJ_INTERFACE_H
#define CARTESIAN_TRAJ_INTERFACE_H

#include "sun_math_toolbox/UnitQuaternion.h"
#include "sun_traj_lib/Traj_Generator_Interface.h"

namespace sun
{
//! Abstract clas representing a Cartesian traj (Position + UnitQuaternion)
class Cartesian_Traj_Interface : public Traj_Generator_Interface
{
private:
  /*!
      Avoid Default constructor
  */
  Cartesian_Traj_Interface();

protected:
  TooN::Vector<6, int> _mask;

public:
  /*======CONSTRUCTORS=========*/

  /*!
      Constructor
  */
  Cartesian_Traj_Interface(double duration, double initial_time = 0.0)
    : Traj_Generator_Interface(duration, initial_time), _mask(TooN::Ones)
  {
  }

  /*!
      Copy Constructor
  */
  // Cartesian_Traj_Interface( const Cartesian_Traj_Interface& traj );

  /*!
      Clone the object in the heap
  */
  virtual Cartesian_Traj_Interface* clone() const = 0;

  /*======END CONSTRUCTORS=========*/

  /*====== GETTERS =========*/

  /*!
      Get the mask at time secs, if mask[i]=0 then the i-th cartesian coordinate should not be taken into account
      NB: last 3 values are related to a quaternion...
  */
  virtual TooN::Vector<6, int> getMask(double secs) const
  {
    return _mask;
  }

  /*====== END GETTERS =========*/

  /*====== SETTERS =========*/

  /*!
      Get the mask at time secs, if mask[i]=0 then the i-th cartesian coordinate should not be taken into account
      NB: last 3 values are related to a quaternion...
  */
  virtual void setMask(TooN::Vector<6, int> mask)
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
    std::cout << TRAJ_ERROR_COLOR "Error in Cartesian_Traj_Interface::changeFrame( TooN::Matrix<4,4> new_T_curr ) | "
                                  "Not implemented..." CRESET
              << std::endl;
    exit(-1);
  }

  /*!
      Change the reference frame of the trajectory
      Apply a rotation matrix to the trajectory
      new_R_curr is the rotation matrix of the current frame w.r.t. the new frame
  */
  virtual void changeFrame(const TooN::Matrix<3, 3>& new_R_curr)
  {
    changeFrame(r2t(new_R_curr));
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
      Get Position at time secs
  */
  virtual TooN::Vector<3> getPosition(double secs) const = 0;

  /*!
      Get Quaternion at time secs
  */
  virtual UnitQuaternion getQuaternion(double secs) const = 0;

  /*!
      Get Linear Velocity at time secs
  */
  virtual TooN::Vector<3> getLinearVelocity(double secs) const = 0;

  /*!
      Get Angular Velocity at time secs
  */
  virtual TooN::Vector<3> getAngularVelocity(double secs) const = 0;

  /*!
      Get Twist Velocity at time secs [ v , w ]^T
  */
  virtual TooN::Vector<6> getTwist(double secs) const
  {
    TooN::Vector<6> t;
    t.slice<0, 3>() = getLinearVelocity(secs);
    t.slice<3, 3>() = getAngularVelocity(secs);
    return t;
  }

};  // END CLASS Cartesian_Traj_Interface

using Cartesian_Traj_Interface_Ptr = std::unique_ptr<Cartesian_Traj_Interface>;

}  // namespace sun

#endif