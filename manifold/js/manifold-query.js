function ManifoldQuery(action, subject, timestamp, filters, params, fields, unique, query_uuid, aq, sq) {  
    // get, update, delete, create
    var action;
    // slice, user, network... 
    var subject; 
    // timestamp, now, latest(cache) : date of the results queried    
    var timestamp;
    // key(field),op(=<>),value
    var filters;
    // todo
    var params;
    // hostname, ip,... 
    var fields;
    // 0,1 : list of element of an object or single object  
    var unique;
    // query_uuid : unique identifier of a query
    var query_uuid;
    // Query : root query (no sub-Query)
    var analyzed_query;
    // {} : Assoc Table of sub-queries ["resources"->subQ1, "users"->subQ2]
    var subqueries;

/*-------------------------------------------------------------
              Query properties are SQL like : 
---------------------------------------------------------------
SELECT fields FROM subject WHERE filter;
UPDATE subject SET field=value WHERE filter; / returns SELECT 
DELETE FROM subject WHERE filter
INSERT INTO subject VALUES(field=value)
-------------------------------------------------------------*/
    
    this.__repr = function () {
	res  = "ManyfoldQuery ";
	res += " id=" + this.query_uuid;
	res += " a=" + this.action;
	res += " s=" + this.subject;
	res += " ts=" + this.timestamp;
	res += " flts=" + this.filters;
	res += " flds=" + this.fields;
	res += " prms=" + this.params;
	return res;
    }	

    this.clone = function() {
        q = new ManifoldQuery();
        return jQuery.extend(true, q, this);
    }
    this.add_filter = function(key, op, value) {
        this.filters.push(new Array(key, op, value));
    }
    this.update_filter = function(key, op, value) {
        // Need to be improved...
        // remove all occurrences of key if operation is not defined
        if(!op){
            this.filters = jQuery.grep(this.filters, function(val, i) {
                return val[0] != key; 
            });
        // Else remove the key+op filters
        }else{
            this.filters = jQuery.grep(this.filters, function(val, i) {return (val[0] != key || val[1] != op);});
        }
        this.filters.push(new Array(key, op, value));
    }

    this.remove_filter = function (key,op,value) {
        // if operator is null then remove all occurences of this key
        if(!op){
            this.filters = jQuery.grep(this.filters, function(val, i) { 
                return val[0] != key; 
            });
        }else{
            this.filters = jQuery.grep(this.filters, function(val, i) {return (val[0] != key || val[1] != op);});
        }
    }

    // FIXME These functions computing diff's between queries are meant to be shared
    this.diff_fields = function (otherQuery) {
        var f1 = this.fields;
        var f2 = otherQuery.fields;

        /* added elements are the ones in f2 not in f1 */
        var added   = jQuery.grep(f2, function (x) { return jQuery.inArray(x, f1) == -1 }); 
        /* removed elements are the ones in f1 not in f2 */
        var removed = jQuery.grep(f1, function (x) { return jQuery.inArray(x, f2) == -1 }); 
        
        return {'added':added, 'removed':removed};
    }

    // FIXME Modify filter to filters
    this.diff_filter = function (otherQuery) {
        var f1 = this.filters;
        var f2 = otherQuery.filters;
        
        /* added elements are the ones in f2 not in f1 */
        var added   = jQuery.grep(f2, function (x) { return !arrayInArray(x, f1)}); 
        /* removed elements are the ones in f1 not in f2 */
        var removed = jQuery.grep(f1, function (x) { return !arrayInArray(x, f2)}); 
        
        return {'added':added, 'removed':removed};
    } 
// we send queries as a json string now 
//    this.as_POST = function() {
//        return {'action': this.action, 'subject': this.subject, 'timestamp': this.timestamp,
//		'filters': this.filters, 'params': this.params, 'fields': this.fields};
//    }
    this.analyze_subqueries = function() {
        /* adapted from the PHP function in com_tophat/includes/query.php */
        var q = new ManifoldQuery();
        q.query_uuid = this.query_uuid;
        q.action = this.action;
        q.subject = this.subject;
        q.timestamp = this.timestamp;

        /* Filters */
        jQuery.each(this.filters, function(i, filter) {
            var k = filter[0];
            var op = filter[1];
            var v = filter[2];
            var pos = k.indexOf('.');
            if (pos != -1) {
                var subject = k.substr(0, pos);
                var field = k.substr(pos+1);
                if (!q.subqueries[subject]) {
                    q.subqueries[subject] = new ManifoldQuery();
                    q.subqueries[subject].action = this.action;
                    q.subqueries[subject].subject = this.subject;
                    q.subqueries[subject].timestamp = this.timestamp;
                }
                q.subqueries[subject].filters.push(Array(field, op, v));
            } else {
                q.filters.push(this.filter);
            }
        });

        /* Params */
        jQuery.each(this.params, function(param, value) {
            var pos = param.indexOf('.');
            if (pos != -1) {
                var subject = param.substr(0, pos);
                var field = param.substr(pos+1);
                if (!q.subqueries[subject]) {
                    q.subqueries[subject] = new ManifoldQuery();
                    q.subqueries[subject].action = this.action;
                    q.subqueries[subject].subject = this.subject;
                    q.subqueries[subject].timestamp = this.timestamp;
                }
                q.subqueries[subject].params[field] = value;
            } else {
                q.params[field] = value;
            }
        });

        /* Fields */
        jQuery.each(this.fields, function(i, v) {
            var pos = v.indexOf('.');
            if (pos != -1) {
                var subject = v.substr(0, pos);
                var field = v.substr(pos+1);
                if (!q.subqueries[subject]) {
                    q.subqueries[subject] = new ManifoldQuery();
                    q.subqueries[subject].action = this.action;
                    q.subqueries[subject].subject = this.subject;
                    q.subqueries[subject].timestamp = this.timestamp;
                }
                q.subqueries[subject].fields.push(field);
            } else {
                q.fields.push(v);
            }
        });
        this.analyzed_query = q;
    }
 
    /* constructor */
    if (typeof action == "undefined")
        this.action = "get";
    else
        this.action = action;
    
    if (typeof subject == "undefined")
        this.subject = null;
    else
        this.subject = subject;

    if (typeof timestamp == "undefined")
        this.timestamp = "now";
    else
        this.timestamp = timestamp;

    if (typeof filters == "undefined")
        this.filters = [];
    else
        this.filters = filters;

    if (typeof params == "undefined")
        this.params = {};
    else
        this.params = params;

    if (typeof fields == "undefined")
        this.fields = [];
    else
        this.fields = fields;

    if (typeof unique == "undefined")
        this.unique = false;
    else
        this.unique = unique;

    this.query_uuid = query_uuid;
    if (typeof analyzed_query == "undefined")
        this.analyzed_query = null;
    else
        this.analyzed_query = aq;

    if (typeof subqueries == "undefined")
        this.subqueries = {};
    else
        this.subqueries = sq;
}  
