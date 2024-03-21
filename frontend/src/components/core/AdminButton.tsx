import ArrowCircleRightIcon from '@mui/icons-material/ArrowCircleRight';
import Button from '@mui/material/Button';
import { useCachedMe } from '@hooks/useCachedMe';


export const generateBaseAdminRedirect = (url: string) => {
    const urlObject = new URL(url);
    const urlPathnameElements = urlObject.pathname.split('/');
    const encodedUUID = urlPathnameElements.pop();

    if (urlPathnameElements.length === 1) {
        return null;
    }

    let decodedUUID;
    try {
        decodedUUID = atob(encodedUUID).split(':')[1];
    } catch (e) {
        return null;
    }

    const urlPathSwitch = urlPathnameElements.slice(4).join('/');
    const adminBaseUrl = `${urlObject.origin}/api/unicorn`;

    switch (urlPathSwitch) {
      case 'registration-data-import':
        return `${adminBaseUrl}/registration_data/registrationdataimport/${decodedUUID}/change`;
      case 'population/household':
        return `${adminBaseUrl}/household/household/${decodedUUID}/change`;
      case 'population/individuals':
        return `${adminBaseUrl}/household/individual/${decodedUUID}/change`;
      case 'details':
        return `${adminBaseUrl}/program/program/${decodedUUID}/change`;
      case 'target-population':
        return `${adminBaseUrl}/targeting/targetpopulation/${decodedUUID}/change`;
      case 'payment-module/payment-plans':
        return `${adminBaseUrl}/payment/paymentplan/${decodedUUID}/change`;
      case 'payment-module/payments':
        return `${adminBaseUrl}/payment/payment/${decodedUUID}/change`;
      case 'grievance/tickets/user-generated':
        return `${adminBaseUrl}/grievance/grievanceticket/${decodedUUID}/change`;
      case 'grievance/tickets/system-generated':
        return `${adminBaseUrl}/grievance/grievanceticket/${decodedUUID}/change`;
      case 'grievance/feedback':
        return `${adminBaseUrl}/accountability/feedback/${decodedUUID}/change`;
      case 'accountability/communication':
        return `${adminBaseUrl}/accountability/message/${decodedUUID}/change`;
      case 'accountability/surveys':
        return `${adminBaseUrl}/accountability/survey/${decodedUUID}/change`;
      default:
        return null;
    }
  };

interface GenericAdminButtonProps {
    currentUrl: string;
}

interface VerificationAdminButtonProps extends GenericAdminButtonProps {
    id: string;
    isPlan?: boolean;
}

export const GenericAdminButton: Button<GenericAdminButtonProps> = ({
    currentUrl,
}) => {
    const { data } = useCachedMe();
    const isSuperUser = data.me.isSuperuser;
    const redirectUrl = generateBaseAdminRedirect(currentUrl);

    if (isSuperUser && redirectUrl) {
        return <a href={redirectUrl}><ArrowCircleRightIcon color="primary"/></a>;
    }
    return null;
};

export const VerificationAdminButton: Button<VerificationAdminButtonProps> = ({
    id,
    currentUrl,
    isPlan = true,
}) => {
    const { data } = useCachedMe();
    const isSuperUser = data.me.isSuperuser;
    const origin = new URL(currentUrl).origin;
    const adminUrl = `api/unicorn/payment/${isPlan ? 'paymentverificationplan' : 'paymentverification'}`;
    const redirectUrl = `${origin}/${adminUrl}/${atob(id).split(':')[1]}`;

    if (isSuperUser) {
        return <a href={redirectUrl}><ArrowCircleRightIcon color="primary" sx={{ ml: 2 }} /></a>;
    }
    return null;
};