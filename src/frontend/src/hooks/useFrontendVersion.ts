//eslint-disable-next-line import/extensions
import packageJson from '../../package.json';

export const useFrontendVersion = (): string => packageJson.version;
