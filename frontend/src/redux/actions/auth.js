import { SIGNUP_SUCCESS, SIGNUP_FAIL } from "./types";

import axios from "axios";

export const signup =
  (first_name, last_name, email, password, re_password) => async (dispatch) => {
    const config = {
      headers: {
        "Content-Type": "application/json",
      },
    };

    const body = JSON.stringify({
      first_name,
      last_name,
      email,
      password,
      re_password,
    });

    try {
      const res = await axios.post(
        `${import.meta.env.VITE_API_URL}/api/auth/users/`,
        body,
        config
      );
      if (res.status === 201) {
        dispatch({
          type: SIGNUP_SUCCESS,
          payload: res.data,
        });
      } else {
        dispatch({
          type: SIGNUP_FAIL,
        });
      }
    } catch (error) {
      dispatch({
        type: SIGNUP_FAIL,
      });
    }
  };
