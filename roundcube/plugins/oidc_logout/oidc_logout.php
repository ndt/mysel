<?php

/**
 *  OIDC logout
 * roundcubemail < version 1.7
 * https://github.com/roundcube/roundcubemail/issues/8057
 */
class oidc_logout extends rcube_plugin
{
    /**
     *  Redirect URL
     */
    private $redirectUrl;

    /**
     *  Init
     */
    public function init()
    {
        $this->add_hook('startup', [ $this, 'handleStartup' ]);
        $this->add_hook('logout_after', [ $this, 'handleLogoutAfter' ]);
    }

    /**
     *  Handle startup and determining redirect URL
     */
    public function handleStartup(array $args)
    {
        if ($args['task'] != 'logout') {
            return;
        }

        $rcmail = rcmail::get_instance();

        // if no logout URI, or no refresh token, safe to give up
        if (!$rcmail->config->get('oauth_logout_uri') || empty($_SESSION['oauth_token']['refresh_token'])) {
            return;
        }

        // if no ID token, refresh token
        if (empty($_SESSION['oauth_token']['id_token'])) {
            $rcmail_oauth = rcmail_oauth::get_instance();
            $rcmail_oauth->refresh_access_token($_SESSION['oauth_token']);
        }

        // generate redirect URL for post-logout
        $params = [
            'post_logout_redirect_uri' => $rcmail->url([], true, true),
            'id_token_hint' => $_SESSION['oauth_token']['id_token'],
        ];

        $this->redirectUrl = $rcmail->config->get('oauth_logout_uri') . '?' . http_build_query($params);
    }

    /**
     *  Handle post-logout redirect
     */
    public function handleLogoutAfter(array $args)
    {
        if (!$this->redirectUrl) {
            return;
        }

        header('Location: ' . $this->redirectUrl, true, 302);
        exit;
    }
}