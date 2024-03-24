import ArrowCircleRightIcon from '@mui/icons-material/ArrowCircleRight';
import { useCachedMe } from '@hooks/useCachedMe';
import * as React from 'react';


interface GenericAdminButtonProps {
    adminUrl: string;
}

export const GenericAdminButton: React.FC<GenericAdminButtonProps> = ({
    adminUrl,
}) => {
    const { data } = useCachedMe();
    const isSuperUser = data.me.isSuperuser;

    if (isSuperUser) {
        return <a href={adminUrl}><ArrowCircleRightIcon color="primary"/></a>;
    }
    return null;
};

export const VerificationAdminButton: React.FC = ({
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