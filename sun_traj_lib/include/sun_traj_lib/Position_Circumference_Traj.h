/*

    Position Circumference Trajectory Generator Class
    This class is generates a circumference trajectory in the cartesian space

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

#ifndef POSITION_CIRCUMFERENCE_TRAJ_H
#define POSITION_CIRCUMFERENCE_TRAJ_H

#include "sun_traj_lib/Position_Traj_Interface.h"
#include "sun_traj_lib/Scalar_Traj_Interface.h"

namespace sun
{
//! Position traj representing a Circumference
class Position_Circumference_Traj : public Position_Traj_Interface
{
private:
  /*!
      No default Constructor
  */
  Position_Circumference_Traj();

  // These vars now are taken from _traj_s
  double _duration, _initial_time;

protected:
  /*!
      Center of the circumference
  */
  TooN::Vector<3> _c;

  /*!
      Radius of the circumference
  */
  double _rho;

  /*!
      Rotation Matrix of the circumference
  */
  TooN::Matrix<3, 3> _R;

  /*!
      Trajectory for the scalar s variable should be a traj from 0 to final_angle
      s = 0 -> _pi   &   s = 1 -> _pf
  */
  Scalar_Traj_Interface_Ptr _traj_s;

public:
  /*======CONSTRUCTORS========*/

  /*!
      Full Constructor
  */
  Position_Circumference_Traj(const TooN::Vector<3>& r_hat, const TooN::Vector<3>& d, const TooN::Vector<3>& pi,
                              const Scalar_Traj_Interface& traj_s);

  /*!
      Compute the params of the circumference given the start point, the final point and radius
      r_hat = normal to the circumference plane
      pi = initial point
      pf = final point
      rho = radius
      c (return param) = center
      angle (return param) = angle to use to generate the scalar trajectory
      sign_plut (optional input) = there are 2 solutions... this bool select the solution
  */
  static void two_points_2_center(const TooN::Vector<3>& r_hat, const TooN::Vector<3>& pi, const TooN::Vector<3>& pf,
                                  double rho, TooN::Vector<3>& c, double& angle, bool sign_plus = true);

  /*!
      Copy Constructor
  */
  Position_Circumference_Traj(const Position_Circumference_Traj& traj);

  /*!
      Clone the object in the heap
  */
  virtual Position_Circumference_Traj* clone() const override;

  /*======END CONSTRUCTORS========*/

  /*====== GETTERS ========*/

  /*!
      Get center of the Circumference
      if the circumferece is a point return The point
  */
  virtual TooN::Vector<3> getCenter() const;

  /*!
      Get orientation of the Circumference as Rotation Matrix
      if the circumferece is a point return Identity
  */
  virtual TooN::Matrix<3, 3> getOrientation() const;

  /*!
      Get radius of the Circumference
      if the circumferece is a point return 0
  */
  virtual double getRadius() const;

  /*!
      check if the circumference is a point
  */
  virtual bool isAPoint() const;

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

  /*====== END GETTERS ========*/

  /*====== SETTERS =========*/

  /*!
      Set the scalar trajectory
      Trajectory for the scalar s variable should be a traj from 0 to final_angle
      s = 0 -> _pi   &   s = 1 -> _pf
      Note: Velocities and accelerations
      TODO!
  */
  virtual void setScalarTraj(const Scalar_Traj_Interface& s_traj);

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
  virtual void changeFrame(const TooN::Matrix<4, 4>& new_T_curr) override;

  /*====== END TRANSFORM =========*/

  /*====== RUNNERS =========*/

  /*!
      Get Position at time secs
  */
  virtual TooN::Vector<3> getPosition(double secs) const override;

  /*!
      Get Velocity at time secs
  */
  virtual TooN::Vector<3> getVelocity(double secs) const override;

  /*!
      Get Acceleration at time secs
  */
  virtual TooN::Vector<3> getAcceleration(double secs) const override;

  /*!
      Get the angular position (position)
  */
  virtual double getAngularPosition(double secs) const;

  /*!
      Get the angular velocity
  */
  virtual double getAngularVelocity(double secs) const;

  /*!
      Get the angular velocity
  */
  virtual double getAngularAcceleration(double secs) const;

  /*====== END RUNNERS =========*/

};  // END CLASS Line_Segment_Traj

using Position_Circumference_Traj_Ptr = std::unique_ptr<Position_Circumference_Traj>;

}  // namespace sun

#endif