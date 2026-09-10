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

#ifndef CARTESIAN_INDEPENDENT_TRAJ_H
#define CARTESIAN_INDEPENDENT_TRAJ_H

#include "sun_traj_lib/Cartesian_Traj_Interface.h"
#include "sun_traj_lib/Position_Traj_Interface.h"
#include "sun_traj_lib/Quaternion_Traj_Interface.h"

namespace sun
{
//! Cartesian Traj made of independent Position an Quaternion trajs
class Cartesian_Independent_Traj : public Cartesian_Traj_Interface
{
private:
  /*!
      Avoid Default constructor
  */
  Cartesian_Independent_Traj();

  // These vars now are taken from _traj_theta
  double _duration, _initial_time;
  TooN::Vector<6, int> _mask;

protected:
  Position_Traj_Interface_Ptr _pos_traj;

  Quaternion_Traj_Interface_Ptr _quat_traj;

public:
  /*======CONSTRUCTORS=========*/

  /*!
      Constructor
  */
  Cartesian_Independent_Traj(const Position_Traj_Interface& pos_traj, const Quaternion_Traj_Interface& quat_traj);

  /*!
      Copy Constructor
  */
  Cartesian_Independent_Traj(const Cartesian_Independent_Traj& traj);

  /*!
      Clone the object in the heap
  */
  virtual Cartesian_Independent_Traj* clone() const override;

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

  /*
      Get the duration [from base class]
  */
  // virtual double getDuration() const;

  /*
      Get the time left [from base class]
  */
  // virtual double getTimeLeft(double secs) const;

  /*====== END GETTERS =========*/

  /*====== SETTERS =========*/

  /*!
      Change the initial time instant (translate the trajectory in the time)
  */
  virtual void changeInitialTime(double initial_time) override;

  /*====== END SETTERS =========*/

  /*====== TRANSFORM =========*/

  /*!
      Change the reference frame of the trajectory
      Apply an homogeneous transfrmation matrix to the trajectory
      new_T_curr is the homog transf matrix of the current frame w.r.t. the new frame
  */
  void changeFrame(const TooN::Matrix<4, 4>& new_T_curr) override;

  /*====== END TRANSFORM =========*/

  /*!
      return true if the trajectory is compleate at time secs
  */
  virtual bool isCompleate(double secs) const override;

  /*!
      return true if the trajectory is started at time secs
  */
  virtual bool isStarted(double secs) const override;

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

  /*
      Get Twist Velocity at time secs [ v , w ]^T
      [from base class]
  */
  // virtual TooN::Vector<6> getTwist(double secs) const override;

};  // END CLASS Cartesian_Independent_Traj

using Cartesian_Independent_Traj_Ptr = std::unique_ptr<Cartesian_Independent_Traj>;

}  // namespace sun

#endif