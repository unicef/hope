import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './utils/en.json';

const resources = {
  en: {
    translation: en,
  },
};

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export default function setupInternalization() {
  return i18n
    .use(initReactI18next) // passes i18n down to react-i18next
    .init({
      resources,
      lng: 'en',
      keySeparator: false, // we do not use keys in form messages.welcome
      interpolation: {
        escapeValue: false, // react already safes from xss
      },
    });
}
