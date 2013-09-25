from django.template.loader      import render_to_string
from django.shortcuts            import render
from django.core.mail            import send_mail

from manifold.core.query         import Query
from manifold.manifoldapi        import execute_query

from portal.models               import PendingSlice
from portal.actions              import authority_get_pi_emails
from portal.forms                import SliceRequestForm
from unfold.loginrequired        import LoginRequiredAutoLogoutView
from myslice.viewutils           import topmenu_items, the_user

class SliceRequestView (LoginRequiredAutoLogoutView):

    def authority_hrn_initial (self, request):
        authorities_query = Query.get('authority').filter_by('authority_hrn', 'included', ['ple.inria', 'ple.upmc']).select('name', 'authority_hrn')
#        authorities_query = Query.get('authority').select('authority_hrn')
        authorities = execute_query(request, authorities_query)
        
        authority_hrn_tuples = [ (authority['authority_hrn'], authority['name'],) for authority in authorities ]
        return {'authority_hrn': authority_hrn_tuples}

    # because we inherit LoginRequiredAutoLogoutView that is implemented by redefining 'dispatch'
    # we cannot redefine dispatch here, or we'd lose LoginRequired and AutoLogout behaviours
    def post (self, request):
        
        # The form has been submitted
        form = SliceRequestForm(request.POST, initial=self.authority_hrn_initial(request)) 

        if form.is_valid():
            slice_name      = form.cleaned_data['slice_name']
            authority_hrn   = form.cleaned_data['authority_hrn']
            number_of_nodes = form.cleaned_data['number_of_nodes']
            type_of_nodes   = form.cleaned_data['type_of_nodes']
            purpose         = form.cleaned_data['purpose']
            
            s = PendingSlice(
                slice_name      = slice_name,
                authority_hrn   = authority_hrn,
                number_of_nodes = number_of_nodes,
                type_of_nodes   = type_of_nodes,
                purpose         = purpose
            )
            s.save()

            # All validation rules pass; process data in form.cleaned_data
            # slice_name, number_of_nodes, type_of_nodes, purpose
            email = form.cleaned_data['email'] # email of the sender
            cc_myself = form.cleaned_data['cc_myself']

            # The recipients are the PI of the authority
            recipients = authority_get_pi_emails(request,authority_hrn)
            #recipients = ['yasin.upmc@gmail.com','jordan.auge@lip6.fr']
            if cc_myself:
                recipients.append(email)
            msg = render_to_string('slice-request-email.txt', form.cleaned_data)
            send_mail("Onelab user %s requested a slice"%email , msg, email, recipients)

            return render(request,'slice-request-ack-view.html') # Redirect after POST
        else:
            return self._display (request, form)

    def get (self, request):
        return self._display (request, SliceRequestForm(initial=self.authority_hrn_initial(request)))

    def _display (self, request, form):
        return render(request, 'slice-request-view.html', {
                'form': form,
                'topmenu_items': topmenu_items('Request a slice', request),
                'username': the_user (request) 
                })


