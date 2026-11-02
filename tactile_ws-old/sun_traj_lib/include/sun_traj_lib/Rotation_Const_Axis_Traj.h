/*

    Rotation Constant Axis Class
    This class is an interface to generate a rotation trajectory in the cartesian space

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

#ifndef ROTATION_CONST_AXIS_TRAJ_H
#define ROTATION_CONST_AXIS_TRAJ_H

#include "sun_traj_lib/Quaternion_Traj_Interface.h"
#include "sun_traj_lib/Scalar_Traj_Interface.h"

namespace sun
{
//! Quaternion traj representing a rotation about a constant axis
class Rotation_Const_Axis_Traj : public Quaternion_Traj_Interface
{
private:
  /*!
      Avoid Default constructor
  */
  Rotation_Const_Axis_Traj();

  // These vars now are taken from _traj_theta
  double _duration, _initial_time;

protected:
  /*!
      Rotation axis
  */
  TooN::Vector<3> _axis;

  /*!
      Initial orientation in quaternion representation
  */
  UnitQuaternion _initial_quat;

  /*!
      Trajectory for the angle variable should be a traj from theta_i to theta_f
      i.e. from the initial angle to the final angle
  */
  Scalar_Traj_Interface_Ptr _traj_theta;

public:
  /*======CONSTRUCTORS=========*/

  /*!
      FULL Constructor
  */
  Rotation_Const_Axis_Traj(const UnitQuaternion& initial_quat, const TooN::Vector<3>& axis,
                           const Scalar_Traj_Interface& traj_theta);

  Rotation_Const_Axis_Traj(const UnitQuaternion& initial_quat, const UnitQuaternion& final_quat,
                           const Scalar_Traj_Interface& traj_theta, double& angle);

  Rotation_Const_Axis_Traj(const Rotation_Const_Axis_Traj& traj);

  /*!
      Clone the object in the heap
  */
  virtual Rotation_Const_Axis_Traj* clone() const override;

  /*======END CONSTRUCTORS=========*/

  /*====== GETTERS =========*/

  /*!
      Get rotation axis
  */
  virtual TooN::Vector<3> getAxis() const;

  /*!
      Get initial quaternion
  */
  virtual UnitQuaternion getInitialQuat() const;

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
      Set rotation axis
  */
  virtual void setAxis(const TooN::Vector<3>& axis);

  /*!
      Set initial quaternion
  */
  virtual void setInitialQuat(const UnitQuaternion& initial_quat);

  /*!
      Change the initial time instant (translate the trajectory in the time)
  */
  virtual void changeInitialTime(double initial_time) override;

  /*!
      Trajectory for the angle variable should be a traj from theta_i to theta_f
      i.e. from the initial angle to the final angle
  */
  virtual void setScalarTraj(const Scalar_Traj_Interface& traj_theta);

  /*====== END SETTERS =========*/

  /*====== TRANSFORM =========*/

  /*!
      Change the reference frame of the trajectory
      Apply a rotation matrix to the trajectory
      new_R_curr is the rotation matrix of the current frame w.r.t. the new frame
  */
  virtual void changeFrame(const TooN::Matrix<3, 3>& new_R_curr) override;

  /*!
      Change the reference frame of the trajectory
      Apply a rotation matrix to the trajectory
      new_Q_curr is the Quaterion representing the rotation matrix of the current frame w.r.t. the new frame
  */
  virtual void changeFrame(const UnitQuaternion& new_Q_curr) override;

  /*====== END TRANSFORM =========*/

  /*!
      Get Delta quaterinion, i.e. initial_Q_now
  */
  virtual UnitQuaternion getDeltaQuat(double secs) const;

  /*!
       Get Quaternion at time secs
  */
  virtual UnitQuaternion getQuaternion(double secs) const override;

  /*!
      Get Angular Velocity at time secs
  */
  virtual TooN::Vector<3> getVelocity(double secs) const override;

  /*!
      Get Angular Acceleration at time secs
  */
  virtual TooN::Vector<3> getAcceleration(double secs) const override;

};  // END CLASS Rotation_Const_Axis_Traj

using Rotation_Const_Axis_Traj_Ptr = std::unique_ptr<Rotation_Const_Axis_Traj>;

}  // namespace sun

#endif