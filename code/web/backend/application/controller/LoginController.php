<?php

/**
 * LoginController
 * Controls everything that is authentication-related
 */
class LoginController extends Controller
{
    /**
     * Construct this object by extending the basic Controller class. The parent::__construct thing is necessary to
     * put checkAuthentication in here to make an entire controller only usable for logged-in users (for sure not
     * needed in the LoginController).
     */
    public function __construct()
    {
        parent::__construct();
    }

    /**
     * Index, default action (shows the login form), when you do login/index
     */
    public function index()
    {
        // if user is logged in redirect to main-page, if not show the view
        if (LoginModel::isUserLoggedIn()) {
            Redirect::home();
        } else {
            $this->View->render('login/index');
        }
    }

    /**
     * The login action, when you do login/login
     */
    public function login()
    {
        // perform the login method, put result (true or false) into $login_successful
        $login_successful = LoginModel::login(
            Request::post('user_name'), Request::post('user_password'), Request::post('set_remember_me_cookie')
        );

        // check login status: if true, then redirect user login/showProfile, if false, then to login form again
        if ($login_successful) {
            Redirect::to('login/showProfile');
        } else {
            Redirect::to('login/index');
        }
    }

    /**
     * The logout action
     * Perform logout, redirect user to main-page
     */
    public function logout()
    {
        LoginModel::logout();
        Redirect::home();
    }

    /**
     * Login with cookie
     */
    public function loginWithCookie()
    {
        // run the loginWithCookie() method in the login-model, put the result in $login_successful (true or false)
         $login_successful = LoginModel::loginWithCookie(Request::cookie('remember_me'));

        // if login successful, redirect to dashboard/index ...
        if ($login_successful) {
            Redirect::to('dashboard/index');
        } else {
            // if not, delete cookie (outdated? attack?) and route user to login form to prevent infinite login loops
            LoginModel::deleteCookie();
            Redirect::to('login/index');
        }
    }

    /**
     * Show user's PRIVATE profile
     * Auth::checkAuthentication() makes sure that only logged in users can use this action and see this page
     */
    public function showProfile()
    {
        Auth::checkAuthentication();
        $this->View->render('login/showProfile', array(
            'user_name' => Session::get('user_name'),
            'user_email' => Session::get('user_email'),
            'user_gravatar_image_url' => Session::get('user_gravatar_image_url'),
            'user_avatar_file' => Session::get('user_avatar_file'),
            'user_account_type' => Session::get('user_account_type')
        ));
    }

    /**
     * Show edit-my-username page
     * Auth::checkAuthentication() makes sure that only logged in users can use this action and see this page
     */
    public function editUsername()
    {
        Auth::checkAuthentication();
        $this->View->render('login/editUsername');
    }

    /**
     * Edit user name (perform the real action after form has been submitted)
     * Auth::checkAuthentication() makes sure that only logged in users can use this action
     */
    public function editUsername_action()
    {
        Auth::checkAuthentication();
        UserModel::editUserName(Request::post('user_name'));
        Redirect::to('login/index');
    }

    /**
     * Show edit-my-user-email page
     * Auth::checkAuthentication() makes sure that only logged in users can use this action and see this page
     */
    public function editUserEmail()
    {
        Auth::checkAuthentication();
        $this->View->render('login/editUserEmail');
    }

    /**
     * Edit user email (perform the real action after form has been submitted)
     * Auth::checkAuthentication() makes sure that only logged in users can use this action and see this page
     */
    // make this POST
    public function editUserEmail_action()
    {
        Auth::checkAuthentication();
        UserModel::editUserEmail(Request::post('user_email'));
        Redirect::to('login/editUserEmail');
    }

    /**
     * Edit avatar
     * Auth::checkAuthentication() makes sure that only logged in users can use this action and see this page
     */
    public function editAvatar()
    {
        Auth::checkAuthentication();
        $this->View->render('login/editAvatar', array(
            'avatar_file_path' => AvatarModel::getPublicUserAvatarFilePathByUserId(Session::get('user_id'))
        ));
    }

    /**
     * Perform the upload of the avatar
     * Auth::checkAuthentication() makes sure that only logged in users can use this action and see this page
     * POST-request
     */
    public function uploadAvatar_action()
    {
        Auth::checkAuthentication();
        AvatarModel::createAvatar();
        Redirect::to('login/editAvatar');
    }

    /**
     * Delete the current user's avatar
     * Auth::checkAuthentication() makes sure that only logged in users can use this action and see this page
     */
    public function deleteAvatar_action()
    {
        Auth::checkAuthentication();
        AvatarModel::deleteAvatar(Session::get("user_id"));
        Redirect::to('login/editAvatar');
    }

    /**
     * Show the change-account-type page
     * Auth::checkAuthentication() makes sure that only logged in users can use this action and see this page
     */
    public function changeUserRole()
    {
        Auth::checkAuthentication();
        $this->View->render('login/changeUserRole');
    }

    /**
     * Perform the account-type changing
     * Auth::checkAuthentication() makes sure that only logged in users can use this action
     * POST-request
     */
    public function changeUserRole_action()
    {
        Auth::checkAuthentication();

        if (Request::post('user_account_upgrade')) {
            // "2" is quick & dirty account type 2, something like "premium user" maybe. you got the idea :)
            UserRoleModel::changeUserRole(2);
        }

        if (Request::post('user_account_downgrade')) {
            // "1" is quick & dirty account type 1, something like "basic user" maybe.
            UserRoleModel::changeUserRole(1);
        }

        Redirect::to('login/changeUserRole');
    }

    /**
     * Register page
     * Show the register form, but redirect to main-page if user is already logged-in
     */
    public function register()
    {
        if (LoginModel::isUserLoggedIn()) {
            Redirect::home();
        } else {
            $this->View->render('login/register');
        }
    }

    /**
     * Register page action
     * POST-request after form submit
     */
    public function register_action()
    {
        $registration_successful = RegistrationModel::registerNewUser();

        if ($registration_successful) {
            Redirect::to('login/index');
        } else {
            Redirect::to('login/register');
        }
    }

    /**
     * Verify user after activation mail link opened
     * @param int $user_id user's id
     * @param string $user_activation_verification_code user's verification token
     */
    public function verify($user_id, $user_activation_verification_code)
    {
        if (isset($user_id) && isset($user_activation_verification_code)) {
            RegistrationModel::verifyNewUser($user_id, $user_activation_verification_code);
            $this->View->render('login/verify');
        } else {
            Redirect::to('login/index');
        }
    }

    /**
     * Show the request-password-reset page
     */
    public function requestPasswordReset()
    {
        $this->View->render('login/requestPasswordReset');
    }

    /**
     * The request-password-reset action
     * POST-request after form submit
     */
    public function requestPasswordReset_action()
    {
        PasswordResetModel::requestPasswordReset(Request::post('user_name_or_email'));
        Redirect::to('login/index');
    }

    /**
     * Verify the verification token of that user (to show the user the password editing view or not)
     * @param string $user_name username
     * @param string $verification_code password reset verification token
     */
    public function verifyPasswordReset($user_name, $verification_code)
    {
        // check if this the provided verification code fits the user's verification code
        if (PasswordResetModel::verifyPasswordReset($user_name, $verification_code)) {
            // pass URL-provided variable to view to display them
            $this->View->render('login/changePassword', array(
                'user_name' => $user_name,
                'user_password_reset_hash' => $verification_code
            ));
        } else {
            Redirect::to('login/index');
        }
    }

    /**
     * Set the new password
     * Please note that this happens while the user is not logged in. The user identifies via the data provided by the
     * password reset link from the email, automatically filled into the <form> fields. See verifyPasswordReset()
     * for more. Then (regardless of result) route user to index page (user will get success/error via feedback message)
     * POST request !
     * TODO this is an _action
     */
    public function setNewPassword()
    {
        PasswordResetModel::setNewPassword(
            Request::post('user_name'), Request::post('user_password_reset_hash'),
            Request::post('user_password_new'), Request::post('user_password_repeat')
        );
        Redirect::to('login/index');
    }

    /**
     * Generate a captcha, write the characters into $_SESSION['captcha'] and returns a real image which will be used
     * like this: <img src="......./login/showCaptcha" />
     * IMPORTANT: As this action is called via <img ...> AFTER the real application has finished executing (!), the
     * SESSION["captcha"] has no content when the application is loaded. The SESSION["captcha"] gets filled at the
     * moment the end-user requests the <img .. >
     * Maybe refactor this sometime.
     */
    public function showCaptcha()
    {
        CaptchaModel::generateAndShowCaptcha();
    }
}
