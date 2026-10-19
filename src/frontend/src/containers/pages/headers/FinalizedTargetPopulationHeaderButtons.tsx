import { HeaderActions } from '@components/core/HeaderActions';
import { HeaderIconAction } from '@components/core/HeaderIconAction';
import { Button } from '@mui/material';
import { FileCopy } from '@mui/icons-material';
import type { ReactElement } from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { DuplicateTargetPopulation } from '../../dialogs/targetPopulation/DuplicateTargetPopulation';
import type { TargetPopulationDetail } from '@restgenerated/models/TargetPopulationDetail';
import { PERMISSIONS } from 'src/config/permissions';

const IconContainer = styled.span`
  button {
    color: #949494;
    min-width: 40px;
    svg {
      width: 20px;
      height: 20px;
    }
  }
`;

export interface FinalizedTargetPopulationHeaderButtonsPropTypes {
  targetPopulation: TargetPopulationDetail;
  canDuplicate: boolean;
}

export function FinalizedTargetPopulationHeaderButtons({
  targetPopulation,
  canDuplicate,
}: FinalizedTargetPopulationHeaderButtonsPropTypes): ReactElement {
  const { t } = useTranslation();
  const [openDuplicate, setOpenDuplicate] = useState(false);

  return (
    <HeaderActions spacing="none">
      {canDuplicate && (
        <HeaderIconAction
          icon={<FileCopy />}
          label={t('Duplicate')}
          onClick={() => setOpenDuplicate(true)}
          dataPerm={PERMISSIONS.TARGETING_DUPLICATE}
        >
          <IconContainer>
            <Button
              data-perm={PERMISSIONS.TARGETING_DUPLICATE}
              onClick={() => setOpenDuplicate(true)}
            >
              <FileCopy />
            </Button>
          </IconContainer>
        </HeaderIconAction>
      )}
      <DuplicateTargetPopulation
        open={openDuplicate}
        setOpen={setOpenDuplicate}
        targetPopulationId={targetPopulation.id}
      />
    </HeaderActions>
  );
}
