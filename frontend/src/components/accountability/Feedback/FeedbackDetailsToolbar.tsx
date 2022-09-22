import { Box, Button } from '@material-ui/core';
import EditIcon from '@material-ui/icons/EditRounded';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { GrievanceTicketQuery } from '../../../__generated__/graphql';
import { BreadCrumbsItem } from '../../core/BreadCrumbs';
import { PageHeader } from '../../core/PageHeader';

interface FeedbackDetailsToolbarProps {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  canEdit: boolean;
}

export const FeedbackDetailsToolbar = ({
  ticket,
  canEdit,
}: FeedbackDetailsToolbarProps): React.ReactElement => {
  const { t } = useTranslation();
  const { id } = useParams();
  const businessArea = useBusinessArea();

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Grievance and Feedback'),
      to: `/${businessArea}/grievance-and-feedback/tickets`,
    },
  ];

  return (
    <PageHeader
      title={`Feedback ID: ${ticket.unicefId}`}
      breadCrumbs={breadCrumbsItems}
    >
      <Box display='flex' alignItems='center'>
        {canEdit && (
          <Box mr={3}>
            <Button
              color='primary'
              variant='outlined'
              component={Link}
              to={`/${businessArea}/feedback/edit-ticket/${id}`}
              startIcon={<EditIcon />}
            >
              {t('Edit')}
            </Button>
          </Box>
        )}
      </Box>
    </PageHeader>
  );
};
