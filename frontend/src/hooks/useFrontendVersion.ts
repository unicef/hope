import packageJson from '../../package.json';

export const useFrontendVersion = (): string => {
  return packageJson.version;
};
