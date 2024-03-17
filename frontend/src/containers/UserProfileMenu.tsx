import {
  Avatar,
  Button,
  ClickAwayListener,
  Grow,
  MenuItem,
  MenuList,
  Paper,
  Popper,
} from '@mui/material';
import * as React from 'react';
import styled from 'styled-components';
import { MeQuery } from '@generated/graphql';
import { clearCache } from '@utils/utils';
import { getClient } from '../apollo/client';
import SendIcon from '@mui/icons-material/Send';

const UserProfileButton = styled(Button)`
  && {
    color: #e3e6e7;
  }
`;
const MenuButtonText = styled.span`
  margin-left: ${({ theme }) => theme.spacing(2)};
`;
interface UserProfileMenuProps {
  meData: MeQuery;
}
export function UserProfileMenu({
  meData,
}: UserProfileMenuProps): React.ReactElement {
  const [open, setOpen] = React.useState(false);
  const anchorRef = React.useRef<HTMLButtonElement>(null);
  // return focus to the button when we transitioned from !open -> open
  const prevOpen = React.useRef(open);
  React.useEffect(() => {
    if (prevOpen.current === true && open === false) {
      anchorRef.current.focus();
    }

    prevOpen.current = open;
  }, [open]);

  const handleToggle = (): void => {
    setOpen((previousOpen) => !previousOpen);
  };

  const handleClearCache = async (): Promise<void> => {
    const client = await getClient();
    await clearCache(client);
  };

  const handleClose = (
    event:
      | React.MouseEvent<HTMLAnchorElement, MouseEvent>
      | React.TouchEvent<HTMLAnchorElement>
      | MouseEvent
      | TouchEvent,
  ): void => {
    if (
      anchorRef.current &&
      anchorRef.current.contains(event.target as HTMLElement)
    ) {
      return;
    }

    setOpen(false);
  };

  const handleLogout = (
    event:
      | React.MouseEvent<HTMLAnchorElement, MouseEvent>
      | React.TouchEvent<HTMLAnchorElement>
      | MouseEvent
      | TouchEvent,
  ): void => {
    window.location.assign('/api/logout');
    localStorage.removeItem('AUTHENTICATED');
    handleClose(event);
    handleClearCache();
  };

  const handleClearCacheAndReloadWindow = async (): Promise<void> => {
    await handleClearCache();
    window.location.reload();
  };

  function handleListKeyDown(event: React.KeyboardEvent): void {
    if (event.key === 'Tab') {
      event.preventDefault();
      setOpen(false);
    }
  }
  if (!meData) {
    return null;
  }

  const handleUrlAdminRedirect = () => {
    const urlObj = new URL(document.location.href);
    console.log(urlObj);

    const urlParts = urlObj.pathname.split('/');
    const encodedObjId = urlParts.pop();
    const objPathname = urlParts.pop();

    switch (objPathname) {
      case 'registration-data-import':
        console.log('registration-data-import');
        break;
      case 'household':
        console.log('household');
        break;
      case 'individuals':
        console.log('individuals');
        break;
      case 'details':
        console.log('programme');
        break;
      case 'target-population':
        console.log('target-population');
        break;
      case 'payment-module/payment-plans':
        console.log('payment-plans');
        break;
      case 'payment-module/payments':
        console.log('payments');
        break;
      case 'payment-verification/payment-plan':
        console.log('verification-items');
        break;
      case 'verification/payment':
        console.log('verification/payment');
        break;
      case 'grievance/tickets/user-generated':
        console.log('grievance/tickets/user-generated');
        break;
      case 'grievance/tickets/system-generated':
        console.log('grievance/tickets/user-generated');
        break;
      case 'grievance/feedback':
        console.log('grievance/feedback');
        break;
      case 'accountability/communication':
        console.log('grievance/feedback');
        break;
      case 'accountability/surveys':
        console.log('grievance/feedback');
        break;
    }
  };

  const adminUrl = handleUrlAdminRedirect();

  return (
    <>
      <UserProfileButton
        ref={anchorRef}
        onClick={handleToggle}
        data-cy="menu-user-profile"
      >
        <Avatar alt={meData.me.email} src="/static/images/avatar/1.jpg" />
        <MenuButtonText> {meData.me.email}</MenuButtonText>
        {meData.me.isSuperuser ? (
          <Button
            variant="outlined"
            size="small"
            color="success"
            href="#outlined-buttons"
            endIcon={<SendIcon />}
            sx={{ ml: 2 }}
        >
          Go to admin
        </Button>
        ) : null }
      </UserProfileButton>
      <Popper
        open={open}
        anchorEl={anchorRef.current}
        role={undefined}
        transition
        disablePortal
      >
        {({ TransitionProps, placement }) => (
          <Grow
            {...TransitionProps}
            style={{
              transformOrigin:
                placement === 'bottom' ? 'center top' : 'center bottom',
            }}
          >
            <Paper>
              <ClickAwayListener onClickAway={handleClose}>
                <MenuList
                  autoFocusItem={open}
                  id="menu-list-grow"
                  onKeyDown={handleListKeyDown}
                >
                  <MenuItem
                    onClick={handleClearCacheAndReloadWindow}
                    data-cy="menu-item-clear-cache"
                  >
                    Clear Cache
                  </MenuItem>
                  <MenuItem
                    href="/api/logout"
                    onClick={handleLogout}
                    data-cy="menu-item-logout"
                  >
                    Logout
                  </MenuItem>
                </MenuList>
              </ClickAwayListener>
            </Paper>
          </Grow>
        )}
      </Popper>
    </>
  );
}
