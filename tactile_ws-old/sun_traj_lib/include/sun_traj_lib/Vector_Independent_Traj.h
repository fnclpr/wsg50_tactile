/*

    Vector Independent Traj Class
    This class generates a vector trajectory basing on independent scalar trajectories

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

#ifndef VECTOR_INDEPENDENT_TRAJ_H
#define VECTOR_INDEPENDENT_TRAJ_H

#include <sun_traj_lib/Scalar_Traj_Interface.h>
#include <sun_traj_lib/Vector_Traj_Interface.h>

namespace sun
{
//! Vectorial Trajectory made of Independent Scalar trajs
class Vector_Independent_Traj : public Vector_Traj_Interface
{
private:
  /*
      Block access to these vars
  */
  double _initial_time, _final_time;

protected:
  /*!
      std::vector containing the trajectories
  */
  std::vector<Scalar_Traj_Interface_Ptr> _traj_vec;

  /* ====== CONSTRUCTORS =======*/

public:
  /*!
      Void Constructor
  */
  Vector_Independent_Traj();

  /*!
      Full constructor
  */
  Vector_Independent_Traj(const std::vector<Scalar_Traj_Interface_Ptr>& traj_vec);

  /*!
      Constructor that creates n equal trajectories
  */
  Vector_Independent_Traj(const Scalar_Traj_Interface& traj, int n);

  /*!
      Copy Constructor
  */
  Vector_Independent_Traj(const Vector_Independent_Traj& traj);

  /*!
      Clone the object in the heap
  */
  virtual Vector_Independent_Traj* clone() const override;

  /* ====== END CONSTRUCTORS =======*/

  /* ====== SETTERS =========*/

  /*!
      Push back a trajectory in the vector
  */
  virtual void push_back_traj(const Scalar_Traj_Interface& traj);

  /*!
      Remove last traj of the vector
  */
  virtual void pop_back_traj();

  /* ====== END SETTERS =========*/

  /*====== GETTERS =========*/

  /*!
      get size of the vector
  */
  virtual int size() const;

  /*!
      Get the final time instant
      It is the max final time
  */
  virtual double getFinalTime() const override;

  /*!
      Get the initial time instant
      It is the min initial time
  */
  virtual double getInitialTime() const override;

  /*
      Get the duration [FROM BASE CLASS]
  */
  // virtual double getDuration() const override;

  /*
      Get the time left [FROM BASE CLASS]
  */
  // virtual double getTimeLeft(double secs) const override;

  /*====== END GETTERS =========*/

  /*====== SETTERS =========*/

  /*!
      Change the initial time instant (translate all the trajectories in the time)
  */
  virtual void changeInitialTime(double initial_time) override;

  /*====== END SETTERS =========*/

  /*!
      return true if all the trajectories are compleate at time secs
  */
  virtual bool isCompleate(double secs) const override;

  /*!
      return true if the at least one trajectory is started at time secs
  */
  virtual bool isStarted(double secs) const override;

  /*====== RUNNERS =========*/

  /*!
      Get Position at time secs
  */
  virtual TooN::Vector<> getPosition(double secs) const override;

  /*!
      Get Velocity at time secs
  */
  virtual TooN::Vector<> getVelocity(double secs) const override;

  /*!
      Get Acceleration at time secs
  */
  virtual TooN::Vector<> getAcceleration(double secs) const override;

  /*====== END RUNNERS =========*/

};  // END CLASS Vector_Independent_Traj

using Vector_Independent_Traj_Ptr = std::unique_ptr<Vector_Independent_Traj>;

}  // namespace sun

#endif