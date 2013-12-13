from unfold.loginrequired               import LoginRequiredAutoLogoutView
#
from manifold.core.query                import Query
from manifold.manifoldapi               import execute_query
from portal.actions                     import manifold_update_user, manifold_update_account
#
from ui.topmenu                         import topmenu_items, the_user
#
from django.http                        import HttpResponse, HttpResponseRedirect
from django.contrib                     import messages
from django.contrib.auth.decorators     import login_required
from django.core.mail                   import send_mail

#
import json, os, re, itertools

# requires login
class AccountView(LoginRequiredAutoLogoutView):
    template_name = "account-view.html"
    
    def dispatch(self, *args, **kwargs):
        return super(AccountView, self).dispatch(*args, **kwargs)


    def get_context_data(self, **kwargs):

        user_query  = Query().get('local:user').select('config','email')
        user_details = execute_query(self.request, user_query)
        
        # not always found in user_details...
        config={}
        for user_detail in user_details:
            #email = user_detail['email']
            if user_detail['config']:
                config = json.loads(user_detail['config'])

        platform_query  = Query().get('local:platform').select('platform_id','platform','gateway_type','disabled')
        account_query  = Query().get('local:account').select('user_id','platform_id','auth_type','config')
        platform_details = execute_query(self.request, platform_query)
        account_details = execute_query(self.request, account_query)
       
        # initial assignment needed for users having no account  
        platform_name = ''
        account_type = ''
        account_usr_hrn = ''
        account_pub_key = ''
        account_reference = ''
        platform_name_list = []
        platform_name_secondary_list = []
        platform_access_list = []
        platform_no_access_list = []
        total_platform_list = []
        account_type_list = []
        account_type_secondary_list = []
        account_reference_list = []
        delegation_type_list = []
        exp_user_cred_list = []
        slice_list = []
        auth_list = []
        slice_cred_exp_list = []
        auth_cred_exp_list = []
        usr_hrn_list = []
        pub_key_list = []
          
        for platform_detail in platform_details:
            if 'sfa' in platform_detail['gateway_type'] and platform_detail['disabled']==0:
                total_platform = platform_detail['platform']
                total_platform_list.append(total_platform)
                
            for account_detail in account_details:
                if platform_detail['platform_id'] == account_detail['platform_id']:
                    platform_name = platform_detail['platform']
                    account_config = json.loads(account_detail['config'])
                    account_usr_hrn = account_config.get('user_hrn','N/A')
                    account_pub_key = account_config.get('user_public_key','N/A')
                    account_reference = account_config.get ('reference_platform','N/A')
                    # credentials
                    acc_slice_cred = account_config.get('delegated_slice_credentials','N/A')
                    acc_auth_cred = account_config.get('delegated_authority_credentials','N/A')

                    if 'N/A' not in acc_slice_cred:
                        for key, value in acc_slice_cred.iteritems():
                            slice_list.append(key)
                            # get cred_exp date
                            exp_date = re.search('<expires>(.*)</expires>', value)
                            if exp_date:
                                exp_date = exp_date.group(1)
                                slice_cred_exp_list.append(exp_date)

                        my_slices = [{'slice_name': t[0], 'cred_exp': t[1]}
                            for t in zip(slice_list, slice_cred_exp_list)]

                    if 'N/A' not in acc_auth_cred:
                        for key, value in acc_auth_cred.iteritems():
                            auth_list.append(key)
                        #get cred_exp date
                            exp_date = re.search('<expires>(.*)</expires>', value)
                            if exp_date:
                                exp_date = exp_date.group(1)
                                auth_cred_exp_list.append(exp_date)

                        my_auths = [{'auth_name': t[0], 'cred_exp': t[1]}
                            for t in zip(auth_list, auth_cred_exp_list)]


                    account_user_credential = account_config.get('delegated_user_credential','N/A')
                    # Expiration date 
                    result = re.search('<expires>(.*)</expires>', account_user_credential)
                    if result:
                        exp_user_cred = result.group(1)
                    # for reference accounts
                    if 'reference' in account_detail['auth_type']:
                        account_type = 'Reference'
                        delegation = 'N/A'
                        platform_name_secondary_list.append(platform_name)
                        account_type_secondary_list.append(account_type)
                        account_reference_list.append(account_reference)
                        secondary_list = [{'platform_name': t[0], 'account_type': t[1], 'account_reference': t[2]} 
                            for t in zip(platform_name_secondary_list, account_type_secondary_list, account_reference_list)]
                       
                    elif 'managed' in account_detail['auth_type']:
                        account_type = 'Principal'
                        delegation = 'Automatic'
                    else:
                        account_type = 'Principal'
                        delegation = 'Manual'
                    # for principal (auth_type=user/managed) accounts
                    if 'reference' not in account_detail['auth_type']:
                        platform_name_list.append(platform_name)
                        account_type_list.append(account_type)
                        delegation_type_list.append(delegation)
                        exp_user_cred_list.append(exp_user_cred)
                        usr_hrn_list.append(account_usr_hrn)
                        pub_key_list.append(account_pub_key)
                        # combining 5 lists into 1 [to render in the template] 
                        lst = [{'platform_name': t[0], 'account_type': t[1], 'delegation_type': t[2], 'credential_expiration':t[3], 'usr_hrn':t[4], 'usr_pubkey':t[5]} 
                            for t in zip(platform_name_list, account_type_list, delegation_type_list, exp_user_cred_list, usr_hrn_list, pub_key_list)]
                    # to hide private key row if it doesn't exist    
                    if 'myslice' in platform_detail['platform']:
                        account_config = json.loads(account_detail['config'])
                        account_priv_key = account_config.get('user_private_key','N/A')
                    if 'sfa' in platform_detail['gateway_type']:
                        platform_access = platform_detail['platform']
                        platform_access_list.append(platform_access)
       
        # Removing the platform which already has access
        for platform in platform_access_list:
            total_platform_list.remove(platform)
        # we could use zip. this one is used if columns have unequal rows 
        platform_list = [{'platform_no_access': t[0]}
            for t in itertools.izip_longest(total_platform_list)]


        context = super(AccountView, self).get_context_data(**kwargs)
        context['data'] = lst
        context['ref_acc'] = secondary_list
        context['platform_list'] = platform_list
        context['my_slices'] = my_slices
        context['my_auths'] = my_auths
        context['person']   = self.request.user
        context['firstname'] = config.get('firstname',"?")
        context['lastname'] = config.get('lastname',"?")
        context['fullname'] = context['firstname'] +' '+ context['lastname']
        context['authority'] = config.get('authority',"Unknown Authority")
        context['user_private_key'] = account_priv_key
        
        # XXX This is repeated in all pages
        # more general variables expected in the template
        context['title'] = 'Platforms connected to MySlice'
        # the menu items on the top
        context['topmenu_items'] = topmenu_items('My Account', self.request)
        # so we can sho who is logged
        context['username'] = the_user(self.request)
#        context ['firstname'] = config['firstname']
        #context.update(page.prelude_env())
        return context


@login_required
#my_acc form value processing
def account_process(request):
    user_query  = Query().get('local:user').select('password','config')
    user_details = execute_query(request, user_query)
    
    account_query  = Query().get('local:account').select('user_id','platform_id','auth_type','config')
    account_details = execute_query(request, account_query)

    platform_query  = Query().get('local:platform').select('platform_id','platform')
    platform_details = execute_query(request, platform_query)

   # for account_detail in account_details:
    #    if account_detail['platform_id'] == 5: 
     #       account_config = json.loads(account_detail['config'])

    if 'submit_name' in request.POST:
        edited_first_name =  request.POST['fname']
        edited_last_name =  request.POST['lname']
        
        config={}
        for user_config in user_details:
        #email = user_detail['email']
            if user_config['config']:
                config = json.loads(user_config['config'])
                config['firstname'] = edited_first_name
                config['lastname'] = edited_last_name
                config['authority'] = config.get('authority','Unknown Authority')
                updated_config = json.dumps(config)
                user_params = {'config': updated_config}
            else: # it's needed if the config is empty 
                user_config['config']= '{"firstname":"' + edited_first_name + '", "lastname":"'+ edited_last_name + '", "authority": "Unknown Authority"}'
                user_params = {'config': user_config['config']} 
        # updating config local:user in manifold       
        #user_params = { 'config': updated_config}
        manifold_update_user(request,user_params)
        # this will be depricated, we will show the success msg in same page
#        return HttpResponse('Sucess: First Name and Last Name Updated!')
        # Redirect to same page with success message
        messages.success(request, 'Sucess: First Name and Last Name Updated.')
        return HttpResponseRedirect("/portal/account/")       
    
    elif 'submit_pass' in request.POST:
        edited_password = request.POST['password']
        
        for user_pass in user_details:
            user_pass['password'] = edited_password
        #updating password in local:user
        user_params = { 'password': user_pass['password']}
        manifold_update_user(request,user_params)
#        return HttpResponse('Success: Password Changed!!')
        messages.success(request, 'Sucess: Password Updated.')
        return HttpResponseRedirect("/portal/account/")

# XXX TODO: Factorize with portal/registrationview.py

    elif 'generate' in request.POST:
        for account_detail in account_details:
            for platform_detail in platform_details:
                if platform_detail['platform_id'] == account_detail['platform_id']:
                    if 'myslice' in platform_detail['platform']:
                        from Crypto.PublicKey import RSA
                        private = RSA.generate(1024)
                        private_key = json.dumps(private.exportKey())
                        public  = private.publickey()
                        public_key = json.dumps(public.exportKey(format='OpenSSH'))
                        # Generate public and private keys using SFA Library
#                        from sfa.trust.certificate  import Keypair
#                        k = Keypair(create=True)
#                        public_key = k.get_pubkey_string()
#                        private_key = k.as_pem()
#                        private_key = ''.join(private_key.split())
#                        public_key = "ssh-rsa " + public_key
                        # now we overwrite the config field with keypair
                        # once there will be user_hrn, we need to keep user_hrn and change only the keypair
                        # see submit_name section for implementing this    
#                       keypair = re.sub("\r", "", keypair)
#                       keypair = re.sub("\n", "\\n", keypair)
#                       #keypair = keypair.rstrip('\r\n')
#                       keypair = ''.join(keypair.split())
                        # updating maniolf local:account table
                        account_config = json.loads(account_detail['config'])
                        # preserving user_hrn
                        user_hrn = account_config.get('user_hrn','N/A')
                        keypair = '{"user_public_key":'+ public_key + ', "user_private_key":'+ private_key + ', "user_hrn":"'+ user_hrn + '"}'
                        updated_config = json.dumps(account_config) 

                        user_params = { 'config': keypair, 'auth_type':'managed'}
                        manifold_update_account(request,user_params)
                        messages.success(request, 'Sucess: New Keypair Generated!')
                        return HttpResponseRedirect("/portal/account/")
        else:
            messages.error(request, 'Account error: You need an account in myslice platform to perform this action')
            return HttpResponseRedirect("/portal/account/")
                       
    elif 'upload_key' in request.POST:
        for account_detail in account_details:
            for platform_detail in platform_details:
                if platform_detail['platform_id'] == account_detail['platform_id']:
                    if 'myslice' in platform_detail['platform']:
                        up_file = request.FILES['pubkey']
                        file_content =  up_file.read()
                        file_name = up_file.name
                        file_extension = os.path.splitext(file_name)[1] 
                        allowed_extension =  ['.pub','.txt']
                        if file_extension in allowed_extension and re.search(r'ssh-rsa',file_content):
                            account_config = json.loads(account_detail['config'])
                            # preserving user_hrn
                            user_hrn = account_config.get('user_hrn','N/A')
                            file_content = '{"user_public_key":"'+ file_content + '", "user_hrn":"'+ user_hrn +'"}'
                            #file_content = re.sub("\r", "", file_content)
                            #file_content = re.sub("\n", "\\n",file_content)
                            file_content = ''.join(file_content.split())
                            #update manifold local:account table
                            user_params = { 'config': file_content, 'auth_type':'user'}
                            manifold_update_account(request,user_params)
                            messages.success(request, 'Publickey uploaded! Please delegate your credentials using SFA: http://trac.myslice.info/wiki/DelegatingCredentials')
                            return HttpResponseRedirect("/portal/account/")
                        else:
                            messages.error(request, 'RSA key error: Please upload a valid RSA public key [.txt or .pub].')
                            return HttpResponseRedirect("/portal/account/")
        else:
            messages.error(request, 'Account error: You need an account in myslice platform to perform this action')
            return HttpResponseRedirect("/portal/account/")

    elif 'dl_pubkey' in request.POST:
        for account_detail in account_details:
            for platform_detail in platform_details:
                if platform_detail['platform_id'] == account_detail['platform_id']:
                    if 'myslice' in platform_detail['platform']:
                        account_config = json.loads(account_detail['config'])
                        public_key = account_config['user_public_key'] 
                        response = HttpResponse(public_key, content_type='text/plain')
                        response['Content-Disposition'] = 'attachment; filename="pubkey.txt"'
                        return response
                        break
        else:
            messages.error(request, 'Account error: You need an account in myslice platform to perform this action')
            return HttpResponseRedirect("/portal/account/")
               
    elif 'dl_pkey' in request.POST:
        for account_detail in account_details:
            for platform_detail in platform_details:
                if platform_detail['platform_id'] == account_detail['platform_id']:
                    if 'myslice' in platform_detail['platform']:
                        account_config = json.loads(account_detail['config'])
                        if 'user_private_key' in account_config:
                            private_key = account_config['user_private_key']
                            response = HttpResponse(private_key, content_type='text/plain')
                            response['Content-Disposition'] = 'attachment; filename="privkey.txt"'
                            return response
                        else:
                            messages.error(request, 'Download error: Private key is not stored in the server')
                            return HttpResponseRedirect("/portal/account/")

        else:
            messages.error(request, 'Account error: You need an account in myslice platform to perform this action')
            return HttpResponseRedirect("/portal/account/")
    
    elif 'delete' in request.POST:
        for account_detail in account_details:
            for platform_detail in platform_details:
                if platform_detail['platform_id'] == account_detail['platform_id']:
                    if 'myslice' in platform_detail['platform']:
                        account_config = json.loads(account_detail['config'])
                        if 'user_private_key' in account_config:
                            for key in account_config.keys():
                                if key== 'user_private_key':    
                                    del account_config[key]
                                
                            updated_config = json.dumps(account_config)
                            user_params = { 'config': updated_config, 'auth_type':'user'}
                            manifold_update_account(request,user_params)
                            messages.success(request, 'Private Key deleted. You need to delegate credentials manually once it expires.')
                            return HttpResponseRedirect("/portal/account/")
                        else:
                            messages.error(request, 'Delete error: Private key is not stored in the server')
                            return HttpResponseRedirect("/portal/account/")
                           
        else:
            messages.error(request, 'Account error: You need an account in myslice platform to perform this action')    
            return HttpResponseRedirect("/portal/account/")
        
    elif 'fuseco' in request.POST:
        # The recipients are the PI of the authority
        #recipients = authority_get_pi_emails(request, authority_hrn)
        recipients = ["support@myslice.info"] 
        requester = request.user # current user
        sender = 'yasin.upmc@gmail.com' # the server email
        msg = "OneLab user %s requested account in fuseco Platform" % requester
        send_mail("Onelab user %s requested an account in Fuseco"%requester , msg, sender, recipients)
        messages.info(request, 'Request to get access on Fuseco platform received. Please wait for PI\'s reply.')
        return HttpResponseRedirect("/portal/account/")

    elif 'ple' in request.POST:
        # The recipients are the PI of the authority
        #recipients = authority_get_pi_emails(request, authority_hrn)
        recipients = ["support@myslice.info"] 
        requester = request.user # current user
        sender = 'yasin.upmc@gmail.com' # the server email
        msg = "OneLab user %s requested account in fuseco Platform" % requester
        send_mail("Onelab user %s requested an account in PLE"%requester , msg, sender, recipients)
        messages.info(request, 'Request to get access on PLE platform received. Please wait for PI\'s reply.')
        return HttpResponseRedirect("/portal/account/")

    elif 'omf' in request.POST:
        # The recipients are the PI of the authority
        #recipients = authority_get_pi_emails(request, authority_hrn)
        recipients = ["support@myslice.info"]
        requester = request.user # current user
        sender = 'yasin.upmc@gmail.com' # the server email
        msg = "OneLab user %s requested account in omf:nitos Platform" % requester
        send_mail("Onelab user %s requested an account in OMF:NITOS"%requester , msg, sender, recipients)
        messages.info(request, 'Request to get access on OMF:NITOS platform received. Please wait for PI\'s reply.')
        return HttpResponseRedirect("/portal/account/")

    elif 'wilab' in request.POST:
        # The recipients are the PI of the authority
        #recipients = authority_get_pi_emails(request, authority_hrn)
        recipients = ["support@myslice.info"]
        requester = request.user # current user
        sender = 'yasin.upmc@gmail.com' # the server email
        msg = "OneLab user %s requested account in Wilab Platform" % requester
        send_mail("Onelab user %s requested an account in Wilab"%requester , msg, sender, recipients)
        messages.info(request, 'Request to get access on Wilab platform received. Please wait for PI\'s reply.')
        return HttpResponseRedirect("/portal/account/")

    elif 'iotlab' in request.POST:
        # The recipients are the PI of the authority
        #recipients = authority_get_pi_emails(request, authority_hrn)
        recipients = ["support@myslice.info"]
        requester = request.user # current user
        sender = 'yasin.upmc@gmail.com' # the server email
        msg = "OneLab user %s requested account in IOTLab Platform" % requester
        send_mail("Onelab user %s requested an account in IOTLab"%requester , msg, sender, recipients)
        messages.info(request, 'Request to get access on IOTLab platform received. Please wait for PI\'s reply.')
        return HttpResponseRedirect("/portal/account/")
  
    else:
        messages.info(request, 'Under Construction. Please try again later!')
        return HttpResponseRedirect("/portal/account/")


