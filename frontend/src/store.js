import { configureStore } from "@reduxjs/toolkit";
import rootReducer from "./redux/reducers";

const store = configureStore({
  reducer: rootReducer,
  // DevTools y thunk están habilitados automáticamente
});

export default store;