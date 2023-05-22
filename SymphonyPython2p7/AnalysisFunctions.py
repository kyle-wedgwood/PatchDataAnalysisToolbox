import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from copy import copy
from scipy.optimize import minimize
from scipy import stats

alpha = 0.05

font = {'family' : 'sans-serif',
        'weight' : 'normal',
        'size'   : 22}

matplotlib.rc('font', **font)

def analyse_data( exp, function_name, data=None, tags=None, include_list=None, \
     user_exclude_list=[], exclude_repeats=True, normalise=False, \
     array_valued=False, **kwargs):
    '''Top level function to analyse data'''
    if data is None:
        data = {}

    exclude_list = copy( user_exclude_list) # This is required to 'reset' the exclude_list
    if not include_list:
        include_list = generate_include_list( exp, tags, exclude_list, exclude_repeats)

    if not include_list:
        raise NoDataError( 'No data to analyse')

    else:
        exp.analyse_data( function_name, data, include_list, **kwargs)

        grouped_data = group_data( data, normalise=normalise, \
                array_valued=array_valued)

        return grouped_data, data


def generate_include_list( exp, tags, exclude_list, exclude_repeats=True):
    '''Generate list of epochs to include in analysis'''
    # Begin by fetching all protocol uuids
    full_list = []
    exp.fetch_protocol_uuids( full_list, exclude_repeats)

    if tags is not None:
        for (tag_name,val) in tags.items():
            exclude_list = exp.check_tag( tag_name, val, exclude_list)


    include_list = [ uuid for uuid in full_list if uuid not in exclude_list]

    return include_list


def compute_mean_IV_curve( exp, folder_name=None, **kwargs):
    '''Computes IV curve averaged over cells'''

    grouped_data,raw_data = analyse_data( exp, 'compute_leak_sub_normalised_current', **kwargs)

    fig, ax = plot_analysed_results( grouped_data)

    ax.set_xlabel( 'Membrane potential (mV)')
    ax.set_ylabel( 'Mean current (pA/pF)')

    ax.axhline( y=0, color='grey', lw=4, ls='--')

    if folder_name:
        fig.savefig( exp.filename + '_averaged_IV_curve.png', bbox_inches='tight')


    return grouped_data, raw_data, fig, ax


def compute_peak_IV_curve( exp, folder_name=None, **kwargs):
    '''Computes IV curve averaged over cells'''

    grouped_data,raw_data = analyse_data( exp, 'compute_leak_sub_normalised_peak_current', **kwargs)

    fig, ax = plot_analysed_results( grouped_data)

    ax.set_xlabel( 'Membrane potential (mV)')
    ax.set_ylabel( 'Peak current (pA/pF)')

    ax.axhline( y=0, color='grey', lw=4, ls='--')

    if folder_name:
        fig.savefig( exp.filename + '_averaged_peak_IV_curve.png', bbox_inches='tight')


    return grouped_data, raw_data, fig, ax


def compute_activation_curve( exp, folder_name=None, **kwargs):
    '''Compute steady state activation curve'''

    grouped_data,raw_data = analyse_data( exp, 'compute_leak_sub_normalised_conductance',\
            normalise=True, **kwargs)

    fig, ax = plot_analysed_results( grouped_data)

    ax.set_xlabel( 'Membrane potential (mV)')
    ax.set_ylabel( '$G/G_{max}$')

    ax.axhline( y=0, color='grey', lw=4, ls='--')

    # Perform fit to activation
    fun = lambda x : np.sum( \
        ( BoltzmannFunction( x, grouped_data['stim']) - grouped_data['mean'])**2)
    res = minimize( fun, x0=[-10,5])

    stimulus_fine = np.arange( start=grouped_data['stim'][0],\
                               stop=grouped_data['stim'][-1], step=0.01)

    ax.plot( stimulus_fine, BoltzmannFunction( res.x, stimulus_fine), \
            color='red', lw=4, dash_capstyle='round')

    if folder_name:
        fig.savefig( exp.filename + '_activation_curve.png', bbox_inches='tight')

    grouped_data['V_half'] = res.x[0]
    grouped_data['k']      = res.x[1]

    return grouped_data, raw_data, ax


def compute_inactivation_curve( exp, folder_name=None, **kwargs):
    '''Compute steady state inactivation curve'''

    grouped_data,raw_data = analyse_data( exp, \
            'compute_normalised_peak_inactivation_current', \
                    normalise=True, **kwargs)

    fig, ax = plot_analysed_results( grouped_data)

    ax.set_xlabel( 'Membrane potential (mV)')
    ax.set_ylabel( '$I/I_{max}$')

    # Perform fit to activation
    fun = lambda x : np.sum( ( \
        BoltzmannFunction( x, grouped_data['stim']) - grouped_data['mean'])**2)
    res = minimize( fun, x0=[-10,-5])

    stimulus_fine = np.arange( start=grouped_data['stim'][0],\
                               stop=grouped_data['stim'][-1], step=0.01)

    ax.plot( stimulus_fine, BoltzmannFunction( res.x, stimulus_fine), \
            color='red', lw=4, dash_capstyle='round')

    if folder_name:
        fig.savefig( exp.filename + '_inactivation_curve.png', bbox_inches='tight')

    grouped_data['V_half'] = res.x[0]
    grouped_data['k']      = res.x[1]

    return grouped_data, raw_data, ax


def compute_inactivation_recovery( exp, folder_name=None, **kwargs):
    '''Compute fast recovery times from inactivation'''

    grouped_data,raw_data = analyse_data( exp, 'compute_peak_current_ratio_fast', \
            normalise=True, **kwargs)

    fig, ax = plot_analysed_results( grouped_data)

    ax.set_xlabel( 'Pulse interval(ms)')
    ax.set_ylabel( 'Current ratio')

    ax.axhline( y=1, color='grey', lw=4, ls='--')

    # Perform fit to recovery times
    fun = lambda x : np.sum( (\
        NegExponential( x, grouped_data['stim']) - grouped_data['mean'])**2)
    res = minimize( fun, x0=[1,-0.2])

    interval_fine = np.arange( start=grouped_data['stim'][0],\
                               stop=grouped_data['stim'][-1], step=0.01)

    ax.plot( interval_fine, NegExponential( res.x, interval_fine), \
            color='red', lw=4, dash_capstyle='round')

    if folder_name:
        fig.savefig( exp.filename + '_inactivation_recovery_curve.png', bbox_inches='tight')


    grouped_data['recovery_fast'] = res.x[1]

    return grouped_data, raw_data, ax


def compute_slow_inactivation_recovery( exp, folder_name=None, **kwargs):
    '''Compute fast recovery times from inactivation'''

    grouped_data,raw_data = analyse_data( exp, 'compute_peak_current_ratio_slow', \
            normalise=True, **kwargs)

    fig, ax = plot_analysed_results( grouped_data)

    ax.set_xlabel( 'Pulse duration (ms)')
    ax.set_ylabel( 'Current ratio')

    ax.axhline( y=1, color='grey', lw=4, ls='--')

    # Perform fit to recovery times
    fun = lambda x : np.sum( \
        ( Exponential( x, grouped_data['stim']) - grouped_data['mean'])**2)
    res = minimize( fun, x0=[0.8,-0.0002])

    duration_fine = np.arange( start=grouped_data['stim'][0],\
                               stop=grouped_data['stim'][-1], step=0.01)

    ax.plot( duration_fine, Exponential( res.x, duration_fine), \
            color='red', lw=4, dash_capstyle='round')

    if folder_name:
        fig.savefig( exp.filename + '_slow_inactivation_recovery_curve.png', bbox_inches='tight')


    grouped_data['recovery_slow'] = res.x[1]

    return grouped_data, raw_data, ax


def compute_whole_cell_conductance( exp, folder_name=None, **kwargs):
    '''Compute whole cell conductance averaged over cells'''

    data = { 0: []}
    grouped_data,raw_data = analyse_data( exp, 'compute_whole_cell_conductance', data, **kwargs)

    # Plot bar chart of results
    ax = boxplot_analysed_results( raw_data, 'Conductance (nS/pF)')

    if folder_name:
        fig.savefig( exp.filename + '_averaged_conductance.png', bbox_inches='tight')


    return raw_data, ax


def compute_maximal_conductance( exp, folder_name=None, **kwargs):
    '''Compute maximal condutance for given inward/outward channel'''

    data = { 'max_conductance': []}
    grouped_data,raw_data = analyse_data( exp, 'compute_normalised_conductance', data, **kwargs)

    max_conductance_ind = np.argmax( np.abs( grouped_data['mean']))
    stim_val = grouped_data['stim'][max_conductance_ind]

    # Plot bar chart of results
    fig, ax = plt.subplots( figsize=(12,8))

    ax.set_ylabel( 'Maximal conductance (nS/pF)')

    ax.boxplot( data[stim_val])

    if folder_name:
        fig.savefig( exp.filename + '_maximal_conductance.png', bbox_inches='tight')


    return raw_data, ax


def compute_gap_junction_current( exp, folder_name=None, **kwargs):
    '''Compute gap junction conductance over all cells'''

    grouped_data,raw_data = analyse_data( exp, 'compute_gap_junction_current', **kwargs)

    fig, ax = plot_analysed_results( grouped_data)

    ax.set_xlabel( 'Transjunctional potential (mV)')
    ax.set_ylabel( 'Conductance (nS/pF)')

    ax.axhline( y=0, color='grey', lw=4, ls='--')

    if folder_name:
        fig.savefig( exp.filename + '_gap_junction_conductance.png', bbox_inches='tight')


    return grouped_data, raw_data, ax


def compute_gap_junction_conductance( exp, folder_name=None, **kwargs):
    '''Compute gap junction conductance over all cells'''

    grouped_data,raw_data = analyse_data( exp, 'compute_gap_junction_conductance', **kwargs)

    fig, ax = plot_analysed_results( grouped_data)

    ax.set_xlabel( 'Transjunctional potential (mV)')
    ax.set_ylabel( 'Conductance (nS/pF)')

    ax.axhline( y=0, color='grey', lw=4, ls='--')

    if folder_name:
        fig.savefig( exp.filename + '_gap_junction_conductance.png', bbox_inches='tight')


    return grouped_data, raw_data, ax


def compute_time_constants( exp, folder_name=None, **kwargs):
    '''Compute time constants for activation and inactivation'''

    grouped_data, raw_data = analyse_data( exp, 'compute_time_constants', array_valued=True, **kwargs)

    fig, ax = plt.subplots( figsize=(12,8))
    ax.set_xlabel( 'Voltage (mV)')
    ax.set_ylabel( 'Time constant (ms)')

    ax.plot( grouped_data['stim'], grouped_data['mean'][:,0], color='blue', \
            lw=4, label='activation')
    ax.errorbar( grouped_data['stim'], grouped_data['mean'][:,0],\
            grouped_data['sem'][:,0], color='blue', capsize=10)
    ax.plot( grouped_data['stim'], grouped_data['mean'][:,1], color='red', \
            lw=4, label='fast inactivation')
    ax.errorbar( grouped_data['stim'], grouped_data['mean'][:,1],\
            grouped_data['sem'][:,1], color='red', capsize=10)
    ax.plot( grouped_data['stim'], grouped_data['mean'][:,2], color='black', \
            lw=4, label='slow inactivation')
    ax.errorbar( grouped_data['stim'], grouped_data['mean'][:,2],\
            grouped_data['sem'][:,2], color='black', capsize=10)

    ax.legend()

    if folder_name:
        fig.savefig( exp.filename + '_time_constants.png', bbox_inches='tight')


    return grouped_data, raw_data, ax


def compute_input_resistance( exp, folder_name=None):
    '''Computes inputs resistance using StepRamp protocol'''
    data = { 0: []}
    grouped_data,raw_data = analyse_data( exp, 'compute_input_resistance', data)

    # Plot bar chart of results
    ax = boxplot_analysed_results( raw_data, 'Input resistance (MOhm)')

    if folder_name:
        fig.savefig( exp.filename + '_input_resistance.png', bbox_inches='tight')


    return raw_data, ax


def compute_resting_potential( exp, folder_name=None):
    '''Computes resting membrane potential using StepRamp protocol'''
    data = { 0: []}
    grouped_data,raw_data = analyse_data( exp, 'compute_resting_potential', data)

    ## Plot bar chart of results
    ax = boxplot_analysed_results( raw_data, 'RMP( mV)')

    if folder_name:
        fig.savefig( exp.filename + '_membrane_capacitance.png', bbox_inches='tight')


    return raw_data, ax


def collate_membrane_capacitance( exp, folder_name=None):
    '''Collects cell membrane capacitances from cell objects'''

    grouped_data,raw_data = analyse_data( exp, 'fetch_membrane_capacitance')

    # Repackage data returned from exp
    data = { 0: []}

    for (key,val) in raw_data.items():
        data[0] = np.append( data[0], np.mean( val))


    ax = boxplot_analysed_results( data, 'Membrane capacitance (pF)')

    if folder_name:
        fig.savefig( exp.filename + '_membrane_capacitance.png', bbox_inches='tight')


    return raw_data, ax


def group_data( data, normalise=False, array_valued=False):
    '''Returns data from analysis functions'''
    stimulus = np.zeros( shape=( len(data)))

    if array_valued:
        for pulse_no, (key, val) in enumerate( data.items()):
            if (pulse_no == 0):
                no_entries = val.shape[1]
                mean_response = np.zeros( shape=( len( data), no_entries))
                std_response = np.zeros( shape=( len(data), no_entries))
                sem_response = np.zeros( shape=( len(data), no_entries))
                no_responses = np.zeros( shape=( len(data), no_entries))


            no_responses[pulse_no] = np.count_nonzero(~np.isnan(val), axis=0)
            stimulus[pulse_no] = key
            mean_response[pulse_no] = np.nanmean( val, axis=0)
            std_response[pulse_no] = np.nanstd( val, axis=0)
            sem_response[pulse_no] = std_response[pulse_no]/np.sqrt( no_responses[pulse_no])


        # Reorder arrays based on stimulus amplitude
        sort_ind = np.argsort( stimulus)

        stimulus = stimulus[sort_ind]
        mean_response = mean_response[sort_ind,:]
        std_response = std_response[sort_ind,:]
        sem_response = sem_response[sort_ind,:]

        grouped_data = { 'stim': stimulus,
                         'mean': mean_response,
                         'std' : std_response,
                         'sem' : sem_response,
                         'N'   : no_responses}

    else:
        mean_response = np.zeros( shape=( len( data)))
        std_response = np.zeros( shape=( len(data)))
        sem_response = np.zeros( shape=( len(data)))
        no_responses = np.zeros( shape=( len(data)))

        for pulse_no, (key, val) in enumerate( data.items()):
            no_responses[pulse_no] = np.count_nonzero(~np.isnan(val))
            stimulus[pulse_no] = key
            mean_response[pulse_no] = np.nanmean( val)
            std_response[pulse_no] = np.nanstd( val)
            sem_response[pulse_no] = std_response[pulse_no]/np.sqrt( no_responses[pulse_no])


        # Reorder arrays based on stimulus amplitude
        sort_ind = np.argsort( stimulus)

        stimulus = stimulus[sort_ind]
        mean_response = mean_response[sort_ind]
        std_response = std_response[sort_ind]
        sem_response = sem_response[sort_ind]

        # Normalise if needed
        if normalise:
            mean_response /= np.max( np.abs( mean_response))

        grouped_data = { 'stim': stimulus,
                         'mean': mean_response,
                         'std' : std_response,
                         'sem' : sem_response,
                         'N'   : no_responses}


    return grouped_data


def boxplot_analysed_results( data, y_label, ax=None, filename=None):
    '''Plot results on axis if specified'''
    if not ax:
        fig, ax = plt.subplots( figsize=(12,8))

    group_names = []
    ticks = range( len( data))
    colors = ['lightsteelblue','firebrick','mediumseagreen' ]
    y_min = 0
    y_max = 0

    if len( data.items()) > 1:
        box_widths = 0.75
    else:
        box_widths = 0.25


    for i, (name,vals) in enumerate( data.items()):

        if name != 0:
            group_names.append( name)

        mean = np.mean( vals)
        std  = np.std( vals)

        if mean+std > y_max:
            y_max = mean+std

        if np.max( vals) > y_max:
            y_max = np.max( vals)

        if mean-std < y_min:
            y_min = mean-std

        if np.min( vals) < y_min:
            y_min = np.min( vals)


        boxprop = { 'linewidth': 0.0,
                    'facecolor': colors[i],
                    'alpha': 0.5}
        whiskprop = { 'linewidth': 1.0,
                      'color': colors[i],
                      'alpha': 0.5}
        meanprop = { 'linewidth': 2.0,
                      'color': 'black',
                      'alpha': 0.5}
        ax.boxplot( vals, meanline=True,
                    showmeans=True, positions=[i], patch_artist=True,
                    showfliers=False, widths=box_widths, meanprops=meanprop,
                    boxprops=boxprop, whiskerprops=whiskprop, capprops=whiskprop)

        x = np.random.normal(i, 0.04, size=len(vals))
        ax.plot( x, vals, color=colors[i], alpha=0.5, marker='.',
             markersize=20, linewidth=0.0)

    ax.set_xlim( [-0.5, len(data)-0.5])
    ax.set_xticks( ticks)
    ax.set_xticklabels( group_names, fontsize=32)

    # Expand y-axis range
    midpoint = (y_max+y_min)/2.0

    y_max -= midpoint
    y_min -= midpoint

    y_max *= 1.1
    y_min *= 1.1

    y_max += midpoint
    y_min += midpoint

    ax.set_ylim( [y_min,y_max])
    ax.set_ylabel( y_label)

      # Now add in significance bars
    y_lim = ax.get_ylim()

    if y_lim[0] > 0:
        y_lim = (0,y_lim[1])

    ax.set_ylim( [y_lim[0], 1.5*y_lim[1]])

    x_lim = ax.get_xlim()
    y_lim = ax.get_ylim()

    x_pos = ticks-x_lim[0]
    x_pos /= (x_lim[1]-x_lim[0])

    y_pos = (0.5*y_lim[1]-y_lim[0])/(y_lim[1]-y_lim[0])

    if len( group_names) == 2:
        t_table = stats.ttest_ind( data[group_names[0]],
                                  data[group_names[1]],
                                  equal_var=True)

        p = t_table.pvalue

        text = 'p = ' + '{:5.4}'.format(p) + '(*)'*bool(p<alpha)
        label_diff(ax,x_pos[0],x_pos[1],y_pos,text,0.07)

    if filename:
        fig.savefig( filename, bbox_inches='tight')


    return ax


def label_diff(ax,x_i,x_j,y,text,adjust):
    '''Adds significance bars to plot'''
    props = {'connectionstyle':'bar','arrowstyle':'-',\
                 'shrinkA':20,'shrinkB':20,'lw':2}

    y += 0.5*adjust
    ax.annotate(text, xy=(0.5,y+0.1+adjust), zorder=10,
                xycoords='axes fraction',ha='center')
    ax.annotate('', xy=(x_i,y), xytext=(x_j,y), arrowprops=props,
                xycoords='axes fraction')


def plot_analysed_results_deprecated( grouped_data, color='black', fig=None, ax=None):
    '''Plots results on axis if specified'''
    if not ax:
        fig, ax = plt.subplots( figsize=(12,8))

    ax.plot( grouped_data['stim'], grouped_data['mean'], \
            color=color, lw=4, dash_capstyle='round')
    ax.errorbar( grouped_data['stim'], grouped_data['mean'],\
            grouped_data['sem'], color=color, capsize=10)

    return fig, ax


def plot_analysed_results( grouped_data_list, curve_labels=None,
        colors=None, xlabel='', ylabel='', fig=None, ax=None, filename=None):
    '''Plots more than one dataset on the same axis''' # could replace the above

    if not ax:
        fig, ax = plt.subplots( figsize=(12,8))


    if (type( grouped_data_list) == dict):
        grouped_data_list = [grouped_data_list]


    no_groups = len( grouped_data_list)

    if not colors:
        colors = ['black']*no_groups


    if not curve_labels:
        curve_labels = [None]*no_groups


    for (grouped_data,color,curve_label) in zip( grouped_data_list, colors, curve_labels):

        ax.plot( grouped_data['stim'], grouped_data['mean'], \
            color=color, lw=4, dash_capstyle='round', label=curve_label)
        ax.errorbar( grouped_data['stim'], grouped_data['mean'],\
            grouped_data['sem'], color=color, capsize=10)


    ax.set_xlabel( xlabel)
    ax.set_ylabel( ylabel)
    if (no_groups > 1):
        ax.legend()

    if filename:
        fig.savefig( filename, bbox_inches='tight')

    return fig, ax


def merge_plots( ax_list, labels, filename=None):
    '''Merges two plots onto same axis'''

    fig, ax_new = plt.subplots( figsize=(12,8))
    color_flag = False

    for ax in ax_list:
        for line in ax.lines:
            color = line.get_color()
            if color_flag & (color == 'red'):
                color = 'blue'

            if color == 'red':
                color_flag = True


            new_line = ax_new.plot( line.get_xdata(), line.get_ydata(),
                  color=color, lw=line.get_lw())

            if (color == 'red'):
                new_line[0].set_label( labels[0])

            elif (color == 'blue'):
                new_line[0].set_label( labels[1])


    ax_new.set_xlabel( ax_list[0].get_xlabel())
    ax_new.set_ylabel( ax_list[0].get_ylabel())
    ax_new.legend()

    if filename:
        fig.savefig( filename, bbox_inches='tight')


    return ax


def combine_data( group_list, normalise=False):
    '''Combines groups of raw data into one'''
    data = {}

    for group in group_list:
        for (key,val) in group.items():
            if key in data.keys():
                data[key] = np.append( data[key], val)
            else:
                data[key] = val

    grouped_data = group_data( data, normalise=normalise)

    return grouped_data, data


def compute_reversal_potential( temp, valence, int_conc, ext_conc):
    '''Compute reversal potential according to Nernst equation'''

    tempKelvin = temp + 273.15
    R = 8.314
    F = 96485

    return 1000*R*tempKelvin/(valence*F)*np.log( ext_conc/int_conc);


def BoltzmannFunction( x, V):
    '''Boltzmann residual function for fitting'''
    return 1.0/( 1.0+np.exp( -(V-x[0])/x[1]))


def NegExponential( a, x):
    '''Monoexponential for fitting recovery'''
    return a[0]*( 1.0-np.exp( a[1]*x))


def Exponential( a, x):
    '''Monoexponential for fitting recovery'''
    return a[0]*np.exp( a[1]*x)


def BiExponential( x, a1, b1, a2, b2, c):
    '''Biexponential with offset for curve fitting'''
    return a1*np.exp( -x/b1) + a2*np.exp( -x/b2) + c


def OffsetExponential( x, a, b, c):
    '''Monoexponential with offset for curve fitting'''
    return a*np.exp( -x/b) + c


# ERROR TYPES
class NoDataError( ValueError): pass
