import { Box, Button, Checkbox, FormControlLabel } from '@material-ui/core';
import React, { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useParams } from 'react-router-dom';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { BreadCrumbsItem } from '../../core/BreadCrumbs';
import { GreyText } from '../../core/GreyText';
import { PageHeader } from '../../core/PageHeader';

interface SetUpPaymentInstructionsHeaderProps {
  baseUrl: string;
  permissions: string[];
  buttons: ReactElement;
}

export const SetUpPaymentInstructionsHeader = ({
  baseUrl,
  permissions,
  buttons,
}: SetUpPaymentInstructionsHeaderProps): React.ReactElement => {
  const location = useLocation();
  const { t } = useTranslation();
  const { id } = useParams();
  const [isChecked, setChecked] = useState(false);
  const [isClosed, setClosed] = useState(
    localStorage.getItem('showDragAndDropInfo') === 'false',
  );
  const isFollowUp = location.pathname.indexOf('followup') !== -1;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: `/${baseUrl}/payment-module/${
        isFollowUp ? 'followup-payment-plans' : 'payment-plans'
      }/${id}`,
    },
  ];

  const handleDoNotShowAgain = (): void => {
    localStorage.setItem('showDragAndDropInfo', 'false');
  };

  const dragAndDropShowInfoComponent = !isClosed ? (
    <Box
      display='flex'
      alignItems='center'
      justifyContent='space-between'
      pl={8}
      pr={8}
      pb={2}
    >
      <GreyText>{t('Drag and drop Payment Instructions to reorder')}</GreyText>
      <Box>
        <FormControlLabel
          label={<GreyText>{t("Don't show again")}</GreyText>}
          control={
            <Checkbox
              color='primary'
              data-cy='checkbox-dont-show-again'
              onChange={(): void => {
                handleDoNotShowAgain();
                setChecked(!isChecked);
              }}
              checked={isChecked}
              inputProps={{ 'aria-labelledby': 'selected' }}
            />
          }
        />
        <Button onClick={() => setClosed(true)}>{t('Close')}</Button>
      </Box>
    </Box>
  ) : null;

  return (
    <PageHeader
      title={t('Set up Payment Instruction')}
      breadCrumbs={
        hasPermissions(PERMISSIONS.PM_VIEW_DETAILS, permissions)
          ? breadCrumbsItems
          : null
      }
      tabs={dragAndDropShowInfoComponent}
    >
      {buttons}
    </PageHeader>
  );
};
