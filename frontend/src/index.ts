import { runWithAdal } from "react-adal";
import { adalInstance } from "./config/adalConfig";

const DO_NOT_LOGIN = false;
runWithAdal(
  adalInstance,
  () => {
    // eslint-disable-next-line
    require("./indexApp.tsx");
  },
  DO_NOT_LOGIN
);
