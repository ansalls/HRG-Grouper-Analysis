'''
    This module sets up the application
'''
import Utils.install_requirements
import Utils.app_setup


def main():
    '''
        Main function to set up the application
    '''
    # Install requirements
    Utils.install_requirements.install_requirements()

    # Run the app setup
    Utils.app_setup.setup()


if __name__ == "__main__":
    main()
