import { AuthenticationContext, adalFetch, withAdalLogin } from "react-adal";
const LOCAL_HOST = "http://localhost:3000";
const redirectUri = () => {
  return process.env.NODE_ENV === "production"
    ? `${process.env.API_BASE_URL}`
    : LOCAL_HOST;
};
export const adalConfig = {
  tenant: "462ad9ae-d7d9-4206-b874-71b1e079776f",
  clientId: "06e50a84-27be-4910-b2ea-43381976c79a",
  redirectUri: redirectUri(),
  endpoints: {
    api: LOCAL_HOST
  },
  cacheLocation: "localStorage",
  postLogoutRedirectUri: redirectUri()
};
export const adalInstance = new AuthenticationContext(adalConfig);
