# Create your views here.

from django.template import RequestContext
from django.shortcuts import render_to_response

from django.contrib.auth.decorators import login_required

from unfold.page import Page
from manifold.manifoldquery import ManifoldQuery

from plugins.stack.stack import Stack
from plugins.hazelnut.hazelnut import Hazelnut 
from plugins.lists.slicelist import SliceList
from plugins.querycode.querycode import QueryCode
from plugins.quickfilter.quickfilter import QuickFilter

from myslice.viewutils import quickfilter_criterias

from myslice.viewutils import topmenu_items, the_user

@login_required
def hazelnut_view (request):
    
    page = Page(request)

    main_query = ManifoldQuery (action='get',
                                subject='resource',
                                timestamp='latest',
                                fields=['hrn','hostname'],
                                filters= [ [ 'slice_hrn', '=', 'ple.inria.omftest', ] ],
                                # xxx filter : should filter on the slices the logged user can see
                                # we don't have the user's hrn yet
                                # in addition this currently returns all slices anyways
                                # filter = ...
                                sort='slice_hrn',
                                )
    page.enqueue_query (main_query)

    main_plugin = Stack (
        page=page,
        title="global container",
        sons=[ 
            Hazelnut ( # setting visible attributes first
                page=page,
                title='a sample and simple hazelnut',
                # this is the query at the core of the slice list
                query=main_query,
                ),
            QueryCode (
                page=page,
                title='xmlrpc code',
                query=main_query,
                ),
            ])

    # variables that will get passed to the view-plugin.html template
    template_env = {}
    
    # define 'unfold1_main' to the template engine
    template_env [ 'unfold1_main' ] = main_plugin.render(request)

    # more general variables expected in the template
    template_env [ 'title' ] = 'Test view for hazelnut'
    # the menu items on the top
    template_env [ 'topmenu_items' ] = topmenu_items('hazelnut', request) 
    # so we can sho who is logged
    template_env [ 'username' ] = the_user (request) 

### #   ########## add another plugin with the same request, on the RHS pane
### #   will show up in the right-hand side area named 'related'
###     related_plugin = SliceList (
###         page=page,
###         title='Same request, other layout',
###         domid='sidelist',
###         with_datatables=True, 
###         header='paginated main',
###         # share the query
###         query=main_query,
###         )
###     # likewise but on the side view
###     template_env [ 'unfold1_margin' ] = related_plugin.render (request)
###     
###     # add our own css in the mix
###     page.add_css_files ( 'css/hazelnut.css')
    
    # don't forget to run the requests
    page.exec_queue_asynchroneously ()

    # xxx create another plugin with the same query and a different layout (with_datatables)
    # show that it worls as expected, one single api call to backend and 2 refreshed views

    # the prelude object in page contains a summary of the requirements() for all plugins
    # define {js,css}_{files,chunks}
    prelude_env = page.prelude_env()
    template_env.update(prelude_env)
    return render_to_response ('view-plugin.html',template_env,
                               context_instance=RequestContext(request))