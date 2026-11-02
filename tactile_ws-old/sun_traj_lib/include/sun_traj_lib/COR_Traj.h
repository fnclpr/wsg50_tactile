/*

    Rotation about a center of rotation - Trajectory Generator Class
    This class is an interface to generate arbitrary cartesian trajectory in the cartesian space
    the angular position is giver as UnitQuaternion

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

#ifndef COR_TRAJ_H
#define COR_TRAJ_H

#include "sun_traj_lib/Cartesian_Traj_Interface.h"
#include "sun_traj_lib/Position_Circumference_Traj.h"

namespace sun
{
//! Cartesian traj representing a rotation about a Center Of Rotation (COR)
class COR_Traj : public Cartesian_Traj_Interface
{
private:
  /*!
      Avoid Default constructor
  */
  COR_Traj();

protected:
  Position_Circumference_Traj _pos_traj;
  TooN::Vector<3> _rot_axis;
  UnitQuaternion _initial_quat;

public:
  /*======CONSTRUCTORS=========*/

  /*!
      Constructor
  */
  COR_Traj(const TooN::Vector<3>& COR, const TooN::Vector<3>& normal, const TooN::Vector<3>& pi,
           const UnitQuaternion& initial_quat, const Scalar_Traj_Interface& traj_theta);

  COR_Traj(const UnitQuaternion& initial_quat, const Position_Circumference_Traj& circ_traj);

  /*!
      Copy Constructor
  */
  COR_Traj(const COR_Traj& traj) = default;

  /*!
      Clone the object in the heap
  */
  virtual COR_Traj* clone() const override;

  /*======END CONSTRUCTORS=========*/

  /*====== GETTERS =========*/

  /*!
      Get the final time instant
  */
  virtual double getFinalTime() const override;

  /*!
      Get the initial time instant
  */
  virtual double getInitialTime() const override;

  /*====== END GETTERS =========*/

  /*====== SETTERS =========*/

  /*!
      Change the initial time instant (translate the trajectory in the time)
  */
  virtual void changeInitialTime(double initial_time) override;

  /*====== END SETTERS =========*/

  /*====== TRANSFORM =========*/

  /*====== END TRANSFORM =========*/

  /*!
      Get Delta quaterinion, i.e. initial_Q_now
  */
  UnitQuaternion getDeltaQuat(double secs) const;

  /*!
      Get Position at time secs
  */
  virtual TooN::Vector<3> getPosition(double secs) const override;

  /*!
      Get Quaternion at time secs
  */
  virtual UnitQuaternion getQuaternion(double secs) const override;

  /*!
      Get Linear Velocity at time secs
  */
  virtual TooN::Vector<3> getLinearVelocity(double secs) const override;

  /*!
      Get Angular Velocity at time secs
  */
  virtual TooN::Vector<3> getAngularVelocity(double secs) const override;

};  // END CLASS COR_Traj

using COR_Traj_Ptr = std::unique_ptr<COR_Traj>;

}  // namespace sun

#endif