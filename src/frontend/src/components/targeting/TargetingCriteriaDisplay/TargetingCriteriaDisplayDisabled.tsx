import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { Tooltip, Box } from '@mui/material';
import { AddCircleOutline } from '@mui/icons-material';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';

export const ContentWrapper = styled(Box)`
  display: flex;
  flex-wrap: wrap;
`;

const IconWrapper = styled.div`
  display: flex;
  color: #a0b6d6;
`;

const AddCriteria = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  color: #003c8f;
  border: 2px solid #a0b6d6;
  border-radius: 3px;
  font-size: 16px;
  padding: ${({ theme }) => theme.spacing(6)}
    ${({ theme }) => theme.spacing(28)};
  cursor: pointer;
  p {
    font-weight: 500;
    margin: 0 0 0 ${({ theme }) => theme.spacing(2)};
  }
`;

function TargetingCriteriaDisplayDisabled({
  showTooltip = false,
}): ReactElement {
  const { t } = useTranslation();
  return (
    <>
      {showTooltip ? (
        <ContentWrapper>
          <Tooltip title="Make sure program has checked household filter flag or individual filter flag">
            <div>
              <AddCriteria
                onClick={() => null}
                data-cy="button-target-population-disabled-add-criteria"
              >
                <IconWrapper>
                  <AddCircleOutline />
                  <p>{t('Add Filter')}</p>
                </IconWrapper>
              </AddCriteria>
            </div>
          </Tooltip>
        </ContentWrapper>
      ) : (
        <ContentWrapper>
          <AddCriteria
            onClick={() => null}
            data-cy="button-target-population-disabled-add-criteria"
          >
            <IconWrapper>
              <AddCircleOutline />
              <p>{t('Add Filter')}</p>
            </IconWrapper>
          </AddCriteria>
        </ContentWrapper>
      )}
    </>
  );
}

export default withErrorBoundary(
  TargetingCriteriaDisplayDisabled,
  'TargetingCriteriaDisplayDisabled',
);
