import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { UserPlus, UserCog, FilePlus2, Users, Package } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';
import { db } from '../services/db';

export default function DashboardHome() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [activity, setActivity] = useState([]);
  const [loading, setLoading] = useState(true);


  useEffect(() => {
    async function loadData() {
      try {
        const statsData = await db.dashboard.getStats();
        // Backend /dashboard/activity returns list of recent transactions
        const activityData = await db.dashboard.getActivity();
        setStats(statsData);
        setActivity(activityData);
      } catch (e) {
        console.error("Dashboard fetch error:", e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
        <p className="text-muted-foreground">Welcome back, Admin. Here's what's happening today.</p>
      </div>

      <motion.div 
        variants={container}
        initial="hidden"
        animate="show"
        className="grid gap-4 md:grid-cols-3"
      >
        <motion.div variants={item} className="cursor-pointer" onClick={() => navigate('/dashboard/party')}>
            <Card className="hover:bg-accent/50 transition-colors border-primary/20 bg-primary/5">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Add Party</CardTitle>
                    <UserPlus className="h-4 w-4 text-primary" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">Add Party</div>
                    <p className="text-xs text-muted-foreground">Register a new client</p>
                </CardContent>
            </Card>
        </motion.div>

        <motion.div variants={item} className="cursor-pointer" onClick={() => navigate('/dashboard/party')}>
            <Card className="hover:bg-accent/50 transition-colors">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Manage Parties</CardTitle>
                    <UserCog className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">Update Party</div>
                    <p className="text-xs text-muted-foreground">Edit details or checks status</p>
                </CardContent>
            </Card>
        </motion.div>

        <motion.div variants={item} className="cursor-pointer" onClick={() => navigate('/dashboard/transactions')}>
            <Card className="hover:bg-accent/50 transition-colors border-purple-500/20 bg-purple-500/5">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">New Rental</CardTitle>
                    <FilePlus2 className="h-4 w-4 text-purple-400" />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">Create Transaction</div>
                    <p className="text-xs text-muted-foreground">Rent items & generate bill</p>
                </CardContent>
            </Card>
        </motion.div>
      </motion.div>

      {/* Quick Stats Overview */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
            <CardHeader>
                <CardTitle>Overview</CardTitle>
            </CardHeader>
            <CardContent className="pl-2">
                {loading ? (
                    <div className="h-[200px] flex items-center justify-center text-muted-foreground">Loading stats...</div>
                ) : (
                    <div className="grid grid-cols-2 gap-4 pt-4 px-4 text-center">
                        <div className="p-4 border rounded-md bg-accent/30">
                            <h3 className="font-semibold text-lg">{stats?.totalItems || 0}</h3>
                            <p className="text-sm text-muted-foreground">Total Items</p>
                        </div>
                        <div className="p-4 border rounded-md bg-accent/30">
                            <h3 className="font-semibold text-lg">{stats?.totalParties || 0}</h3>
                            <p className="text-sm text-muted-foreground">Total Parties</p>
                        </div>
                        <div className="p-4 border rounded-md bg-accent/30">
                            <h3 className="font-semibold text-lg">{stats?.activeParties || 0}</h3>
                            <p className="text-sm text-muted-foreground">Active Parties</p>
                        </div>
                        <div className="p-4 border rounded-md bg-accent/30">
                            <h3 className="font-semibold text-lg">{stats?.totalRentedOutQty || 0}</h3>
                            <p className="text-sm text-muted-foreground">Items Rented</p>
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
        <Card className="col-span-3">
             <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>
                    {activity.length} recent transactions.
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    {loading ? (
                       <p className="text-sm text-muted-foreground">Loading activity...</p>
                    ) : activity.length === 0 ? (
                       <p className="text-sm text-muted-foreground">No recent activity.</p>
                    ) : (
                        activity.slice(0, 5).map((act, index) => (
                            <div key={index} className="flex items-center">
                                <div className="ml-4 space-y-1">
                                    <p className="text-sm font-medium leading-none">{act.PartyName || 'Unknown Party'}</p>
                                    <p className="text-sm text-muted-foreground">{act.itemQty} x {act.Item || `Item #${act.itemId}`}</p>
                                </div>
                                <div className="ml-auto font-medium">{act.rentAmount ? `+₹${act.rentAmount}` : 'Return'}</div>
                            </div>
                        ))
                    )}
                </div>
            </CardContent>
        </Card>
      </div>
    </div>
  );
}
